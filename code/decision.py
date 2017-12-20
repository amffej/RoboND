import numpy as np

# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.nav_angles is not None:
        # Check for Rover.mode status
        if Rover.mode == 'forward': 
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:  
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else: # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                # Set steering to average angle clipped to the range +/- 15
                #Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                #HUG LEFT WALL
                x = 8
                Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi) + x , -15, 15)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'
        # If we are stuck lets do some stuff
        elif Rover.mode == 'ImStuck':
            #print('Trying to get unstuck')
            targetangle = Rover.stuckyaw+180
            if targetangle > 360:
                    targetangle = targetangle - 360

            if Rover.sequence == 1: ### STEP ###
                Rover.step_time = Rover.total_time
                Rover.sequence_try = 2
                Rover.sequence = 6    

            elif Rover.sequence == 2: ### STEP ###
                step_time = 10
                if Rover.vel > -0.5 and Rover.total_time - Rover.step_time < step_time:
                    Rover.throttle = -1
                    Rover.brake = 0
                    Rover.steer = 0
                else:
                    Rover.throttle = 0
                    Rover.sequence_try = 3
                    Rover.sequence = 6                 
                    
            elif Rover.sequence == 3: ### STEP ###
                step_time = 15 #Time Limit to execute step (Seconds)
                if Rover.yaw > targetangle and Rover.total_time - Rover.step_time < step_time:
                    Rover.steer = -15
                    Rover.throttle = 0
                    Rover.brake = 0
                else:
                    Rover.sequence_try = 4
                    Rover.sequence = 6    

            elif Rover.sequence == 4: ### STEP ###
                step_time = 20
                if Rover.vel < 0.2 and Rover.total_time - Rover.step_time < step_time:
                    Rover.throttle_set = 1
                    Rover.throttle = Rover.throttle_set
                else:
                    Rover.sequence_try = 5
                    Rover.sequence = 6
            
            elif Rover.sequence == 5: ### STEP ###
                step_time = 25
                if Rover.vel < 0.5 and Rover.total_time - Rover.step_time < step_time:
                    Rover.throttle = 1
                    Rover.brake = 0
                    Rover.steer = 0
                else:
                    Rover.sequence_try = 6
                    Rover.throttle = 0
                    Rover.sequence = 6 
            
            elif Rover.sequence == 6: ### STEP ###
                Rover.throttle_set = 0.3
                Rover.brake = Rover.brake_set
                Rover.sequence = Rover.sequence_try
                if Rover.sequence_try == 6:
                    Rover.sequence_try = 1   
                Rover.mode = 'forward'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    Rover.steer = -15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'
    # Just to make the rover do something 
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = 0
        
    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True
    
    # Determine if we are stuck
    if Rover.vel == 0  and Rover.throttle > 0:
        if Rover.total_time > 5:
            Rover.stuckyaw = Rover.yaw
            #Rover.sequence = 1;
            print('Robot Stuck at:  ', Rover.stuckyaw) 
            Rover.mode = 'ImStuck'
        
    return Rover

