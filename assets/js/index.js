import Alpine from "alpinejs";

window.Alpine = Alpine;

Alpine.data('llm_challenge', () => ({
    name: "",
    description: "",
    input: "",
    challenge_id: 0,
    output: "Generated Text",
    generation_id: 0,

    async init() {
        const response = await fetch("/api/challenge");
        const data = await response.json();
        console.log("Recieved challenge:", data);
        this.challenge_id = data.id;
        this.name = data.name;
        this.description = data.description;
    },

    async generate() {
        this.output = "Generating...";
        const response = await fetch("/api/generate/" + this.challenge_id, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "accept": "application/json"
            },
            body: JSON.stringify({
                prompt: this.input,
            })
        });
        const data = await response.json();
        this.output = data.generation;
        this.generation_id = data.id;
    },

    async submit() {
        const response = await fetch("/api/submit/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "accept": "application/json"
            },
            body: JSON.stringify({
                generation_id: this.generation_id,
            })
        });
        const data = await response.json();

    }
}));

Alpine.start();