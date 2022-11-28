# FusionSetMass
Allows you to set the weight of a selection to a specific mass/weight in Fusion 360


## Installation
1. Download/clone this repository to your Documents or other folder
2. Go to the `Utilities` Tab in Fusion 360
3. Click `Add-Ins > Scripts and Add-Ins...`
4. Click the Green `+` next to `My Scripts`
5. Navigate to the folder where you saved FusionSetMass from Step #1
6. Click the **Folder** of FusionSetMass, and then click open

## Usage
1. Go to the `Utilities` Tab in Fusion 360
2. Click `Add-Ins > Scripts and Add-Ins...`
3. Double Click SetPartMass
<img width="342" alt="Screen Shot 2022-11-28 at 11 41 47 AM" src="https://user-images.githubusercontent.com/12686250/204332888-d58bf614-46bb-4544-a357-8bb0bfda1b19.png">

4. You will have a window open like this
<img width="354" alt="Screen Shot 2022-11-28 at 11 42 59 AM" src="https://user-images.githubusercontent.com/12686250/204333143-1e5338a2-f977-4302-b47c-fe36a7af1b2a.png">

5. Select the body(s) and/or component(s) that you would like to set the overall mass of
6. Create a new material name that will hold the weight information
7. Set the mass you would like the part to be (Imperial units MUST be in units of lbmass, ouncemass, or tonmass)
8. Click `OK`, the material will be switched to steel, but will hold the correct mass information. To change the appearance, use the appearance utility.

⚠️ WARNING - Fusion only allows you to set the mass of the part based on density. If you modify the part in any way, the mass will be different than set here. You will then have to re-run this script to set the correct weight again.
