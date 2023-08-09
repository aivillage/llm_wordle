# llm_wordle
Challenges for LLM

# Building
Copy `.env_dev.template` to `.env_dev` then put your HF key in. Then run `docker compose -f dockers/docker-compose.dev.yml up --build` in one terminal, and in another terminal run `./build.sh` to update the JavaScript, or `npx tailwindcss -i ./assets/css/styles.css -o ./app/static/css/styles.css --watch` to work on the CSS.

## Static files

All static files (JS, images) are in the assets directory. During the build process of the alpineJS (with `npm run build`) the directory gets copied over to `app/static`. The CSS gets built seperately with the tailwind build process with `npx tailwindcss -i ./assets/css/styles.css -o ./app/static/css/styles.css` and also copied over. 

If the images are not showing up, run the `npm run build`. 


If you want to use a different CSS for the index put it in the `assets/css` directory and then edit `vite.config.js` to make sure it gets copied over during the `npm run build`. 