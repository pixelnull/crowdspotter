```
_________                               .___  _________                  __     __                   
\_   ___ \ _______   ____  __  _  __  __| _/ /   _____/______    ____  _/  |_ _/  |_   ____  _______ 
/    \  \/ \_  __ \ /  _ \ \ \/ \/ / / __ |  \_____  \ \____ \  /  _ \ \   __\\   __\_/ __ \ \_  __ \
\     \____ |  | \/(  <_> ) \     / / /_/ |  /        \|  |_> >(  <_> ) |  |   |  |  \  ___/  |  | \/
 \______  / |__|    \____/   \/\_/  \____ | /_______  /|   __/  \____/  |__|   |__|   \___  > |__|   
        \/                               \/         \/ |__|                               \/         
```

CrowdSpotter: CrowdStrike Online Host Monitor (Windows Version)

Author: [@pixelnull@infosec.exchange](https://infosec.exchange/@pixelnull)

This script monitors the online status of specified hosts using the CrowdStrike Falcon API.
It periodically checks the status of the hosts and alerts the user when a host comes online
or goes offline. It will link online hosts to the the Host Managment page in the CrowdStrike
Web Console. There are two scripts, one for Windows and one for Linux.

Before running the script:
1. Replace the placeholder values for CLIENT_ID and CLIENT_SECRET above with your actual API credentials.

To run the script:
1. Ensure you have Python installed on your Windows system.
2. Install the required packages:

   `pip install crowdstrike-falconpy`
3. Run the script with one or more AIDs as arguments:

   `python crowdspotter.py aid1 aid2 aid3 ...`

The script will:
- Check host statuses at specified interval. Defualt is 30 seconds.
- Print an alert message when a new host comes online.
- Link to the host in Host Managment page in CrowdStrike's Web Console.
- Play a sound alert if the system is capable.
- Continue running until you press Ctrl+C to stop it.

This will probably not be updated if it breaks unless I still need it later.

License:  CrowdSpotter © 2024 by [@pixelnull@infosec.exchange](https://infosec.exchange/@pixelnull) is licensed under Creative
Commons Attribution-ShareAlike 4.0 International. To view a copy of this license,
visit https://creativecommons.org/licenses/by-sa/4.0/
