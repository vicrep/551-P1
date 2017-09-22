# COMP 515 P1 code and utils


### Setup

Requires Python v3.6.


```bash
$ pip install -r requirements.txt
```

Please excuse the hardcoded secrets, trying to make our lives easier.

You will also need to [setup a Reddit app](https://www.reddit.com/prefs/apps/) too access their API. Once you have your app's client ID and secret, set them using the environment variables `REDDIT_CLIENT_ID` and `REDDIT_SECRET`, respectively.

### Collecting data

```python
import data_collection
import json

submissions_tree = get_submissions()

# serialize and store to file:
with open('output.json', 'w') as output_file:
    json.dump(submissions_tree,
              output_file
              outsort_keys=True,
              indent=4)
```

### Formatting and curating data

```python
import Data_Formatting

formatData('input.json', 'output.xml')

```
