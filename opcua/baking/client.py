import time

from opcua import Client, ua
import inquirer
import socket
import json

from recipe import Recipe

# OPCUA server address
SERVER_ENDPOINT = "opc.tcp://localhost:4841/freeopcua/server/"

# OPCUA object details
OBJECT_NAME = "MyObject"
NAMESPACE_URI = "http://examples.freeopcua.github.io"

# TCP server details
TCP_SERVER_IP = "localhost"
TCP_SERVER_PORT = 9999


def send_anomaly_data(anomaly_coordinates=None, anomaly_sleep_durations=None):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((TCP_SERVER_IP, TCP_SERVER_PORT))
    data = {
        'anomaly_coordinates': anomaly_coordinates,
        'anomaly_sleep_durations': anomaly_sleep_durations,
    }
    client.send(json.dumps(data).encode())
    client.close()


def main():
    client = Client(SERVER_ENDPOINT)
    try:
        client.connect()

        # Get the root node
        root = client.get_root_node()
        print("Root node is: ", root)

        # Get namespace index
        uri = NAMESPACE_URI
        idx = client.get_namespace_index(uri)

        # Access the ProcessState variable and ArmX, ArmY, ArmZ
        myobject = root.get_child(["0:Objects", f"{idx}:{OBJECT_NAME}"])
        process_state = myobject.get_child([f"{idx}:ProcessState"])
        recipe = myobject.get_child([f"{idx}:Recipe"])
        arm_x = myobject.get_child([f"{idx}:ArmX"])
        arm_y = myobject.get_child([f"{idx}:ArmY"])
        arm_z = myobject.get_child([f"{idx}:ArmZ"])
        proximity_sensor = myobject.get_child([f"{idx}:ProximitySensor"])
        gripper_state = myobject.get_child([f"{idx}:VacuumGripperState"])

        anomaly_coordinates = [None, None, None]

        while True:
            # Inquirer
            questions = [
                inquirer.List('action',
                              message="Choose an action",
                              choices=['Set ProcessState', 'Set Recipe', 'Raise Continuous Anomaly',
                                       'Raise State Anomaly', 'Exit'],
                              ),
            ]

            answers = inquirer.prompt(questions)

            if answers['action'] == 'Set ProcessState':
                process_questions = [
                    inquirer.List('process',
                                  message="What state do you want to set for the process?",
                                  choices=['True', 'False'],
                                  ),
                ]

                process_answers = inquirer.prompt(process_questions)
                if process_answers['process'].lower() == 'true':
                    process_state.set_value(True)
                elif process_answers['process'].lower() == 'false':
                    process_state.set_value(False)
                print(f"ProcessState has been set to {process_answers['process']}")

            elif answers['action'] == 'Set Recipe':
                recipe_questions = [
                    inquirer.List('recipe',
                                  message="What recipe do you want to set?",
                                  choices=list(Recipe) + ['Custom'],
                                  ),
                ]

                recipe_answers = inquirer.prompt(recipe_questions)
                if recipe_answers['recipe'] == 'Custom':
                    custom_recipe_question = [
                        inquirer.Text('custom_recipe', message="Enter your custom recipe"),
                    ]
                    custom_recipe_answer = inquirer.prompt(custom_recipe_question)
                    recipe.set_value(custom_recipe_answer['custom_recipe'])
                    print(f"Recipe has been set to {custom_recipe_answer['custom_recipe']}")
                else:
                    recipe.set_value(recipe_answers['recipe'])
                    print(f"Recipe has been set to {recipe_answers['recipe']}")
            elif answers['action'] == 'Raise Continuous Anomaly':
                # Select variable to raise anomaly for
                anomaly_questions = [
                    inquirer.Checkbox('variables',
                                      message="For which variable(s) do you want to raise an anomaly?",
                                      choices=['ArmX', 'ArmY', 'ArmZ'],
                                      ),
                ]

                anomaly_answers = inquirer.prompt(anomaly_questions)
                print(anomaly_answers)

                for var in anomaly_answers['variables']:
                    anomaly_value = float(input(f"Enter anomaly value for {var}: "))

                    if var == 'ArmX':
                        anomaly_coordinates[0] = anomaly_value
                    elif var == 'ArmY':
                        anomaly_coordinates[1] = anomaly_value
                    elif var == 'ArmZ':
                        anomaly_coordinates[2] = anomaly_value

                anomaly_duration = float(input(f"Enter anomaly duration in seconds: "))
                send_anomaly_data(anomaly_coordinates=anomaly_coordinates)
                time.sleep(anomaly_duration)
                anomaly_coordinates = [None, None, None]
                send_anomaly_data(anomaly_coordinates=anomaly_coordinates)
            elif answers['action'] == 'Raise State Anomaly':
                anomaly_questions = [
                    inquirer.Checkbox('variables',
                                      message="For which state variable(s) do you want to raise an anomaly?",
                                      choices=['RobotState', 'ProximitySensor', 'VacuumGripperState'],
                                      ),
                ]

                anomaly_answers = inquirer.prompt(anomaly_questions)
                anomaly_sleep_durations = [None, None, None]
                for var in anomaly_answers['variables']:
                    if var == 'RobotState':
                        robot_state_questions = [
                            inquirer.Checkbox('robot_state',
                                              message="Choose a state for the robot",
                                              choices=['PICK', 'PLACE', 'REST'],
                                              ),
                        ]
                        robot_state_answers = inquirer.prompt(robot_state_questions)
                        print(robot_state_answers)
                        for state in robot_state_answers['robot_state']:
                            if state == 'PICK':
                                anomaly_value = float(input(f"Enter anomaly sleep duration for {state}: "))
                                anomaly_sleep_durations[0] = anomaly_value
                            elif state == 'PLACE':
                                anomaly_value = float(input(f"Enter anomaly sleep duration for {state}: "))
                                anomaly_sleep_durations[1] = anomaly_value
                            elif state == 'PLACE':
                                anomaly_value = float(input(f"Enter anomaly sleep duration for {state}: "))
                                anomaly_sleep_durations[2] = anomaly_value
                        sleep_dur = float(input(f"Enter waiting period to set back to normal values: "))
                        send_anomaly_data(anomaly_sleep_durations=anomaly_sleep_durations)
                        time.sleep(sleep_dur)
                        anomaly_sleep_durations = [None, None, None]
                        send_anomaly_data(anomaly_sleep_durations=anomaly_sleep_durations)
                    elif var == 'ProximitySensor':
                        proximity_sensor_questions = [
                            inquirer.List('proximity_sensor_state',
                                          message="Choose a state for the proximity sensor",
                                          choices=['True', 'False', 'Custom'],
                                          ),
                        ]
                        proximity_sensor_answers = inquirer.prompt(proximity_sensor_questions)

                        if proximity_sensor_answers['proximity_sensor_state'] == 'Custom':
                            custom_value = input("Enter your custom value: ")
                            # Cast the custom value to a Boolean type if it's 'True' or 'False'
                            if custom_value.lower() == 'true':
                                proximity_sensor.set_value(True)
                            elif custom_value.lower() == 'false':
                                proximity_sensor.set_value(False)
                            else:
                                proximity_sensor.set_value(custom_value)
                        elif proximity_sensor_answers['proximity_sensor_state'] == 'True':
                            proximity_sensor.set_value(True)
                        else:  # 'False' case
                            proximity_sensor.set_value(False)
                    elif var == 'VacuumGripperState':
                        vacuum_gripper_state_questions = [
                            inquirer.List('vacuum_gripper_state',
                                          message="Choose a state for the vacuum gripper",
                                          choices=['True', 'False', 'Custom'],
                                          ),
                        ]
                        vacuum_gripper_state_answers = inquirer.prompt(vacuum_gripper_state_questions)

                        if vacuum_gripper_state_answers['vacuum_gripper_state'] == 'Custom':
                            custom_value = input("Enter your custom value: ")
                            # Cast the custom value to a Boolean type if it's 'True' or 'False'
                            if custom_value.lower() == 'true':
                                gripper_state.set_value(True)
                            elif custom_value.lower() == 'false':
                                gripper_state.set_value(False)
                            else:
                                gripper_state.set_value(custom_value)
                        elif vacuum_gripper_state_answers['vacuum_gripper_state'] == 'True':
                            gripper_state.set_value(True)
                        else:  # 'False' case
                            gripper_state.set_value(False)

            elif answers['action'] == 'Exit':
                break
    finally:
      client.disconnect()

if __name__ == "__main__":
    main()
