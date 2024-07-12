# PSM
- Decide on major feature for 0.3
- Check out if tab Widgets actually size properly once I have accounted for using the addWidget() function instead of the setCentralWidget() function

# FLTR
- Set favourites/pins
- Create user contract material delta tracker (Possibly for future contract manager)
- Implement ability to delete items from route (or clear route)
- Implement ability to toggle which arrival time display format the player wants to see (I.e. time remaining or time of arrival)
- If arrival Time is before Current Time, display that the ship has arrived, but data is stale (User probably has yet to log in)
- Have tool put username into shipdata so that username appears even when userdict could not load.
- Use scrollarea
- Set up Time To Arrival to match PMMG
- Decide what a Simple view will look like.
    - Implement a choice between simple/expanded view.
- Figure out if animating Routes is feasible

- Store fetched ship data (Like segments) longterm to collect permanent information that can be extrapolated into data

# PDM
- ## Start Versioning!
- Develop a proper user configuration API
    - create PDM-QT to give the PDM a reusable Qt interface for configuring it. 
- Create or use a custom logging library function that lets me specify levels of verbosity instead of just having static print functions
- Create a dedicated set of initX methods that wrap around and only call fetchX if it hasn't happened yet, to allow multiple modules that may not necessarily be working with each other to request the PDM initialise certain datas as needed, without actually fetching them several times, or regrouping all of the loading calls into the highest-level widget's initialisation function.
- **Eventually:** subdivide the gargantuan library into several submodules

# DSC
- Show Total tonnage and volume of currently loaded shipment
- Overhaul UI to match FLTR
- Deprecate use of MaterialDisplay; Instead utilise a custom widget and mimick the FLTR setup.