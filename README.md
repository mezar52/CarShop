# Car shop

### **Description**:

This is a training project that emulates an auto store.
The project uses such services as: AWS S3, Heroku and Mailjet.
Supports databases: SQILite3 and PostgreSQL
Also, this project has its own API, the work of which corresponds to the way the main views work. To try to use the api,
just add the /api prefix to the url. API has a swagger.

Also E2E and Unit tests are written for the project to run which you need to write: `pytest`.
**Attention: `E2E tests will not work if the local server is turned off`.** 

**Black in github** action is used for code formatting.

### How to run this project:

1. Install dependencies:
    ```
     pip install -r requirements.txt
    ```

2. Apply migration:

    ```
    python manage.py migrate
    ```

3. For the project functions to work it is necessary to set the following variables:
   ##### Mac&Linux:
   ```
   export MONOBANK_TOKEN="your_token"
   export AWS_S3_ACCESS_KEY_ID="your_access_key"
   export AWS_S3_SECRET_ACCESS_KEY="your_secret_access_key"
   export GOOGLE_CLIENT_ID="your_client_id"
   export GOOGLE_CLIENT_SECRET="your_client_secret"
   export MAILJET_API_KEY="your_api_key"
   export MAILJET_API_SECRET="your_api_secret"
   ```

   ##### Windows:
   ```
   $Env:MONOBANK_TOKEN="your_token"
   $Env:AWS_S3_ACCESS_KEY_ID="your_access_key"
   $Env:AWS_S3_SECRET_ACCESS_KEY="your_secret_access_key"
   $Env:GOOGLE_CLIENT_ID="your_client_id"
   $Env:GOOGLE_CLIENT_SECRET="your_client_secret"
   $Env:MAILJET_API_KEY="your_api_key"
   $Env:MAILJET_API_SECRET="your_api_secret"
   ```

4. Use a custom command to create demo data
   #### Attention: if you have not entered your credentials from AWS S3 then it will not be possible to use the custom command.

   ```
    python manage.py generate_data
   ```

5. Run the local server to see the result

   ```
   python manage.py runserver 
   ```
   
6. To run the tests, write to the console: 
   ```
   pytest
   ```