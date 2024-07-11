# FLTR
- Create user contract material delta tracker (Possibly for future contract manager)
- ~~Implement Auto-formatting where relevant~~
- Implement ability to delete items from route (or clear route)
- ~~Finalise Route Dialog Functionality~~
- ~~Use labels instead of QDateTimeEdit, so that I'm not limited by formatting.~~
- Implement countdown toggle for the arrival time
- ~~Decide on Format Text~~
- Have tool put username into shipdata so that username appears even when userdict could not load.

# PDM
- ~~Create function that returns the game-format of the location string you used (turns hrt -> HRT)~~
- Create or use a custom logging library function that lets me specify levels of verbosity instead of just having static print functions
- Create a dedicated set of initX methods that wrap around and only call fetchX if it hasn't happened yet, to allow multiple modules that may not necessarily be working with each other to request the PDM initialise certain datas as needed, without actually fetching them several times, or regrouping all of the loading calls into the highest-level widget's initialisation function.
- **Eventually:** subdivide the gargantuan library into several submodules

# DSC
- Show Total tonnage and volume of currently loaded shipment
- Overhaul UI to match FLTR
- Deprecate use of MaterialDisplay; Instead utilise a custom widget and mimick the FLTR setup.