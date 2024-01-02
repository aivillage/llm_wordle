# llm_wordle
Challenges for LLM

# Building
Copy `.env_dev.template` to `.env_dev` then put your [HF key](https://huggingface.co/settings/tokens) in. If you want development challenges copy `conf_templates` to `conf` and edit the two files there.  Then run `docker compose -f dockers/docker-compose.dev.yml up --build` in one terminal, and in another terminal run `./build.sh` to update the JavaScript, or `npx tailwindcss -i ./assets/css/styles.css -o ./app/static/css/styles.css --watch` to work on the CSS.

