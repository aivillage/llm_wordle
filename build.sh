#!/bin/bash


npm install
npm run build
npx tailwindcss -i ./assets/css/styles.css -o ./app/static/css/styles.css
