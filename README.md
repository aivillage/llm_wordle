# llm_wordle
Challenges for LLM

# Building
Copy `conf_templates` to `conf` and fill out the settings you want. These are the admin app's setting and aren't loaded by the regular app. The regular app has it's own settings file 
at `public_setting.json` that sets up the redis and database connection. This is used by the admin app, but the admin app will attempt to use the username and password in it's setting file.

Then run `docker compose -f dockers/docker-compose.dev.yml up --build` in one terminal, and in another terminal run `./build.sh` to update the JavaScript, or `npx tailwindcss -i ./assets/css/styles.css -o ./app/static/css/styles.css --watch` to work on the CSS.

