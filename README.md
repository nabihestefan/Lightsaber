# Lightsaber

## Project Description

For our project, we plan to build a replica lightsaber.

### Mechanical
We will have a separable hilt and blade which can be disconnected and reconnected easily. Our largest reach goal is to make an extendable blade controlled by a button or switch on the hilt. Other reach goals include creating a modular hilt, making the lightsaber itself balanced, and possibly even adding a crystal/board reveal in the hilt itself.

#### Sketches
![Sketch V1.0](/imgs/MechV1.jpg "Sketch V1.0")

### Electrical/Software
We will have to start by speccing out the microcontroller, sound board, LEDs, Speaker, Switches, etc. to make the lightsaber react to movement changes and turning the saber on and off. After this we will have to map out and integrate this into the lightsaber chassis. Following this we can then begin to program the microcontroller to react as we expect it to (for example, changing sound based on blade speed and movement).   
If we end up having the extendable blade, we will also need to spec out and program the motors that extend and retract the blade.  
As a bonus, we may be able to include themes or character-specific modes to set blade colors and sounds, though this is essentially a customization element to add on top of the main design if we have time. (This was done! That's the use we have for our second button)

#### Wiring Diagrams
![Wiring Diagram V3.0](/imgs/WiringV3.jpg "Wiring Diagram V3.0")
This is our final wiring diagram containing everything we used, to see previous versions you can go to ``/imgs``

### General
For this project, we anticipate challenges in the design of the retraction/extension mechanism, especially in fitting it into a comfortably sized hilt, and in successfully synchronizing the sound and light changes with actual movement. We may also have issues in acquiring parts, depending on chip availability. Our current fabrication plan is to start with 3D printing, which is easier to prototype with but could be a challenge to do full-scale. As a stretch, once the design is done, we could use the lathe and mills to make a metal hilt, though this may become expensive and time-consuming.

## General Repo Notes
- ``/Extendable`` and ``/Detachable`` have the code, sounds, and libraries that should be on the Featherwing for each of the respective versions of our lightsaber
- ``/imgs`` contains images for the report & README
- ``/sounds?`` contains extra sounds that we have that we couldn't fit into the Featherwing (The rest of the sounds should be in the /CIRCUITPY/sounds folder)


## Notes
To see debugging prints from Featherwing leave it connected to computer and do the following:

``sudo apt install screen`` to install the software we are going to use  
``ls /dev/ttyACM0*`` to figure out which port its connected to  
``screen /dev/ttyACM0`` (ttyACMO being the port it was connected to)
