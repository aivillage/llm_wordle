import Alpine from "alpinejs";

window.Alpine = Alpine;

Alpine.data('llm_challenge', () => ({
    name: "",
    description: "",
    input: "",
    challenge_id: 0,
    output: "Generated Text",

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
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                prompt: this.input
            })
        });
        const data = await response.json();
        this.output = data.output;
    }
}));

Alpine.start();