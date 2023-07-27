# llm_wordle
Challenges for LLM

# Building
Copy `conf_templates` to `conf` and fill out the settings you want. These are the admin app's setting and aren't loaded by the regular app. The regular app has it's own settings file 
at `public_setting.json` that sets up the redis and database connection. This is used by the admin app, but the admin app will attempt to use the username and password in it's setting file.

In one terminal run `pip install -r requirements.txt`, then `uvicorn users:app --reload`

To build the javascript and move everything into the correct static directory run `./build.sh`. Rerun this to rebuild the js. This needs `npm`

To just mess with the templates and not touch the JS run: `npx tailwindcss -i ./assets/css/styles.css -o ./app/static/css/styles.css --watch`

