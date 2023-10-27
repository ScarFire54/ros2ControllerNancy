# ros2ControllerNancy

##  Step before launching ROS2 humble installer script

Get this repo on your computer
`git clone https://github.com/ScarFire54/ros2ControllerNancy`

Launch this command to consider theses files as script and run them after going into the folder created :

`chmod u+x ros2_installer`
`chmod u+x RSP_comm_builder`
`./ros2_installer`
`./RSP_comm_builder`

Then you can go inside the rsp_comm folder

### Need to set path to the build in .bashrc or repeat the command source install/setup.bash each time
`echo "source ~/ros2ControllerNancy/rsp_comm/install/setup.bash" >> ~/.bashrc`

## Commands to run turtlebot 3 pi waffle in 3 differents terminals

`ros2 launch turtlebot3_bringup turtlebot3_state_publisher.launch.py`
`ros2 launch turtlebot3_bringup robot.launch.py`
`ros2 run rsp_comm rosController`
