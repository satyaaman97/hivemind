# Clone Investopedia API and Setup Local Environment

Source: https://github.com/dchrostowski/investopedia_simulator_api

When running `install_investopedia_api.sh`, you might come across this error
```
ERROR: No matching distribution found for pkg-resources 
```

To fix it, change directory into `investopedia_simulator_api` after cloning and remove this line 
`pkg-resources` from the requirements.txt and run the script again. 

If you get error like this when running `python3 hivemind_trading.py` 
```
No module named 'api_models'
```

add these lines to `investopedia_api.py` in **investopedia_simulator_api** folder.

```
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))
```
