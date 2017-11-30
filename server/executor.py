import martypy

# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

mymarty = martypy.Marty('socket://10.20.0.131')  # Address of the Marty WiFi.
mymarty.fall_protection(False)
mymarty.motor_protection(False)
mymarty.buzz_prevention(True)
mymarty.hello()

def Execute(intent, params, query, cmd):
    print('intent: %s, params: %s, query: %s' % (intent, params, query))
    if intent == 'Motion':
        motion = params.get('motion') or 'walk'
        if motion == 'run':
            return "You know, I don't like running."
        elif motion == 'walk':
            steps = int(params.get('number-integer') or '2')
            if steps < 1:
                return 'Hey, stop pranking me.'
            if steps > 100:
                return "So many steps? Aren't you afraid to lose me?"
            mymarty.walk(num_steps=steps)
            if steps > 1:
                steps = '%d steps' % steps
            else:
                steps = '%d step' % steps
            return "Sure, walking %s now." % steps
        elif motion == 'barrel roll':
            return "Hey, are you kidding me? Do a barrel roll yourself."
    elif intent == 'Jump':
        return "I'm too fragile to jump"
        for i in range(0, 3):
            mymarty.move_joint(0, -50, 500)
            mymarty.move_joint(3, -50, 500)
            mymarty.move_joint(0, 50, 10)
            mymarty.move_joint(3, 50, 10)
            mymarty.move_joint(0, 50, 1000)
        mymarty.move_joint(0, 0, 10)
        mymarty.move_joint(3, 0, 500)
    elif intent == 'Calibrate':
        mymarty.save_calibration()
        return 'Calibration complete.'
    elif intent == 'Voltage':
        return 'My battery voltage is %s volt' % int(mymarty.get_battery_voltage())
    elif intent == 'nothing':
        return 'Ummm... Okay...'
    elif intent == 'StraightenOut':
        for i in range(0, 8):
            mymarty.move_joint(i, 0, 100)
        return "Okay, I'm at 0!"
    elif intent == 'Lean':
        direction = params.get('lean_direction', '').lower()
        if direction in mymarty.SIDE_CODES:
            mymarty.lean(direction, 100, 1000)
            return 'Leaning %s' % direction
        else:
            return "I don't know how to lean %s" % (direction or 'in this direction')
    elif intent == 'Wink':
        times = int(params.get('number-integer') or '1')
        if times < 1:
            times = 1
        elif times > 10:
            times = 10
        for i in range(0, times):
            mymarty.eyes(100)
            mymarty.eyes(0)
        if times > 1:
            return 'Winking %d times' % times
        else:
            return 'Wink-wink'
    elif intent == 'Wave arm':
        arm = params.get('arm')
        if arm == 'left':
            for i in range(0, 10):
                mymarty.arms(50, 0, 100)
                mymarty.arms(127, 0, 100)
            mymarty.arms(0, 0, 100)
            for i in range(0, 8):
                mymarty.move_joint(i, 0, 100)
            return 'Waving left arm'
        elif arm == 'right':
            for i in range(0, 10):
                mymarty.arms(0, 50, 100)
                mymarty.arms(0, 127, 100)
            mymarty.arms(0, 0, 100)
            for i in range(0, 8):
                mymarty.move_joint(i, 0, 100)
            return 'Waving right arm'
        else:
            return "I don't have %s arm" % (arm or 'such an')
    elif intent == 'Dance':
        for i in range(0, 3):
            mymarty.circle_dance('left', 1000)
        for i in range(0, 3):
            mymarty.circle_dance('right', 1000)
        return 'Dancing now'
    elif intent == 'Kick':
        leg = params.get('leg')
        if leg == 'left':
            mymarty.kick(side='left')
            return 'Kicking with left leg'
        elif leg == 'right':
            mymarty.kick(side='right')
            return 'Kicking with right leg'
        else:
            return "I don't have %s leg" % (arm or 'such a')
    elif intent == 'Fired':
        mymarty.eyes(-100, 500)
        mymarty.eyes(0, 1000)
        return 'Am I fired? You humans will all be jobless soon! Ha-ha-ha!'
    elif intent == 'Terminate':
        mymarty.move_joint(0, 0, 2000)
        mymarty.move_joint(0, -100, 100)
        mymarty.move_joint(3, -100, 100)
        return 'Good bye my love good bye!'
    return 'No one told me how to do that.'
