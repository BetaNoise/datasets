import urllib3
import requests
import random
import time
import json
import pandas as pd
import datetime
urllib3.disable_warnings()

base_url = 'https://weavesocks.g5k.lan'
sleep_time = 570  # sleep for 9.5 minutes in between cycles (30s latency, so 10 mins in total)
cycles = 180  # 10*6 = 1 hour * 30 = 30 hours (1 measurement)

pages = [
    'index.html',
    'category.html',
    'category.html?tags=blue',
    'category.html?tags=brown',
    'category.html?tags=green',
    'category.html?tags=short',
    'category.html?tags=toes',
    'category.html?tags=magic',
    'category.html?tags=formal',
    'category.html?tags=smelly',
    'detail.html?id=510a0d7e-8e83-4193-b483-e27e09ddc34d',
    'detail.html?id=03fef6ac-1896-4ce8-bd69-b798f85c6e0b',
    'detail.html?id=3395a43e-2d88-40de-b95f-e00e1502085b',
    'detail.html?id=837ab141-399e-4c1f-9abc-bace40296bac'
]

users = [
    {
        'username': 'john',
        'email': 'john@doe.ie',
        'firstName': 'John',
        'lastName': 'Doe'
    },
    {
        'username': 'jane',
        'email': 'jane@doe.ie',
        'firstName': 'Jane',
        'lastName': 'Doe'
    },
    {
        'username': 'spongebob',
        'email': 'spongebob@bikinibottom.ie',
        'firstName': 'Spongebob',
        'lastName': 'Squarepants'
    }
]

cart_items = [
    "3395a43e-2d88-40de-b95f-e00e1502085b",
    "808a2de1-1aaa-4c25-a9b9-6612e8f29a38"
]

response_df = pd.DataFrame(columns=['Time', 'Type', 'Response', 'Code'])

error_count = 0
for cycle in range(cycles):
    print('Generating traffic...')
    try:
        for public_traffic in range(0, 300):
            page = random.choice(pages)
            r = requests.get(f'{base_url}/{page}', verify=False)
            try:
                status_code = int(r.status_code)
            except:
                status_code = 0
            public_df = pd.DataFrame([[str(datetime.datetime.now()), 'Public', float(r.elapsed.total_seconds()), status_code]], columns=['Time', 'Type', 'Response', 'Code'])
            response_df = pd.concat([response_df, public_df])
            time.sleep(0.1)

        for user in users:
            if cycle == 0:
                s = requests.Session()
                # Create users
                r = s.post(f'{base_url}/register', verify=False,
                    data={'username': user['username'],'password': 'password','email': user['email'],'firstName': user['firstName'],'lastName': user['lastName']})
                try:
                    status_code = int(r.status_code)
                except:
                    status_code = 0
                register_df = pd.DataFrame([[str(datetime.datetime.now()), 'Register', float(r.elapsed.total_seconds()), status_code]], columns=['Time', 'Type', 'Response', 'Code'])
                response_df = pd.concat([response_df, register_df])
                user['session'] = s
                time.sleep(0.5)
            else:
                s = user['session']

            # Add 5 random items to cart
            item = random.choice(cart_items)
            for random_items in range(5):
                r = s.post(f'{base_url}/cart', verify=False,
                    headers={'Content-Type': 'application/json; charset=UTF-8'},
                    data=json.dumps({'id':item}))
                try:
                    status_code = int(r.status_code)
                except:
                    status_code = 0
                cart_post_df = pd.DataFrame([[str(datetime.datetime.now()), 'Cart (POST)', float(r.elapsed.total_seconds()), status_code]], columns=['Time', 'Type', 'Response', 'Code'])
                response_df = pd.concat([response_df, cart_post_df])

            # List cart
            r = s.get(f'{base_url}/cart')
            try:
                status_code = int(r.status_code)
            except:
                status_code = 0
            cart_get_df = pd.DataFrame([[str(datetime.datetime.now()), 'Cart (GET)', float(r.elapsed.total_seconds()), status_code]], columns=['Time', 'Type', 'Response', 'Code'])
            response_df = pd.concat([response_df, cart_get_df])
    except requests.exceptions.RequestException as e:
        error_count += 1
        print(error_count)
        if error_count > 29:
            print("Traffic generation failed 30 times, exiting")
            exit(-1)
        else:
            continue
    
    # Every hour
    if (cycle + 1) % 6 == 0:
        # Save responses to .CSV file
        file_name = "hour" + str(cycle // 6 - 1)
        response_df.to_csv(f'{file_name}.csv', index=True)
        # Reset the DF
        response_df = pd.DataFrame(columns=['Time', 'Type', 'Response', 'Code'])


    # Sleep for next cycle, but the last
    if cycle != cycles-1:
        print('Sleeping')
        time.sleep(sleep_time)
    else:
        print('Done')
        break
