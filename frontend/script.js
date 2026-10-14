
// Stage 20 — Connect the Frontend with the Backend API

// const API_URL = "http://127.0.0.1:8000";

const API_URL = window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : window.location.origin;

// Get the required HTML elements
const form = document.getElementById("predictionForm");
const predictBtn = document.getElementById("predictBtn");
const sampleBtn = document.getElementById("sampleBtn");


const normalSampleBtn = document.getElementById("normalSampleBtn");
const failureSampleBtn = document.getElementById("failureSampleBtn");


const apiStatus = document.getElementById("apiStatus");
const apiMessage = document.getElementById("apiMessage");
const resultPanel = document.getElementById("resultPanel");
const message = document.getElementById("message");

// Display success and error messages
function showMessage(text, type = "") {
    message.textContent = text;
    message.className = "message " + type;
}

// Data Engineering — Load actual records from the AI4I 2020 CSV dataset
let datasetOffset = 0;

// Data Engineering — Load actual records from the CSV dataset


async function loadSample(mode = "any") {
    const buttons = [sampleBtn, normalSampleBtn, failureSampleBtn];

    buttons.forEach(button => button.disabled = true);

    const clickedButton =
        mode === "normal" ? normalSampleBtn :
            mode === "failure" ? failureSampleBtn :
                sampleBtn;

    const originalText = clickedButton.textContent;
    clickedButton.textContent = "Loading...";

    try {
        // Load actual records from the CSV dataset.
        // For "any", alternate between normal and failure records.
        let selectedMode = mode;

        if (mode === "any") {
            const nextMode =
                sessionStorage.getItem("nextAnySampleMode") || "normal";

            selectedMode = nextMode;

            sessionStorage.setItem(
                "nextAnySampleMode",
                nextMode === "normal" ? "failure" : "normal"
            );
        }

        const url = selectedMode === "failure"
            ? `${API_URL}/machines?limit=100&offset=0&failure_only=true`
            : `${API_URL}/machines?limit=100&offset=0`;

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error("Could not load dataset records.");
        }

        const result = await response.json();

        let candidates = result.machines || [];

        // Keep only records matching the selected historical outcome.
        candidates = candidates.filter(machine =>
            Number(machine["Machine failure"]) ===
            (selectedMode === "failure" ? 1 : 0)
        );

        if (candidates.length === 0) {
            throw new Error(
                `No ${selectedMode} records were found in the returned data.`
            );
        }

        // Rotate through records each time the same type is requested.
        const indexKey = `sampleIndex_${selectedMode}`;
        const index = Number(sessionStorage.getItem(indexKey) || 0);
        const sample = candidates[index % candidates.length];

        sessionStorage.setItem(indexKey, String(index + 1));

        // Fill the dashboard with actual CSV sensor readings.
        document.getElementById("machine_type").value = sample["Type"];
        document.getElementById("air_temperature").value =
            sample["Air temperature [K]"];
        document.getElementById("process_temperature").value =
            sample["Process temperature [K]"];
        document.getElementById("rotational_speed").value =
            sample["Rotational speed [rpm]"];
        document.getElementById("torque").value = sample["Torque [Nm]"];
        document.getElementById("tool_wear").value = sample["Tool wear [min]"];

        // Hide the previous prediction until the new sample is tested.
        resultPanel.hidden = true;

        showMessage(
            `Loaded UDI ${sample["UDI"]}. Historical outcome: ` +
            `${Number(sample["Machine failure"]) === 1 ? "FAILURE" : "NORMAL"}. ` +
            "Click Predict Machine Failure to get the model prediction.",
            "success"
        );

    } catch (error) {
        showMessage("Could not load sample: " + error.message, "error");
    } finally {
        buttons.forEach(button => button.disabled = false);
        clickedButton.textContent = originalText;
    }
}

// Cloud Engineering — Check whether the API is available
async function checkApi() {
    try {
        const response = await fetch(`${API_URL}/health`);

        if (!response.ok) {
            throw new Error("Health endpoint returned an error.");
        }

        const data = await response.json();

        apiStatus.textContent =
            data.model_loaded && data.dataset_loaded
                ? "Connected"
                : "Partially available";

        apiMessage.textContent =
            data.model_loaded && data.dataset_loaded
                ? `API, model and dataset are ready (${data.dataset_records} records)`
                : "Check the backend model and dataset";

    } catch (error) {
        apiStatus.textContent = "Offline";
        apiMessage.textContent = "Start the FastAPI backend";
    }
}

// Load a dataset record when the Load Sample button is clicked
// sampleBtn.addEventListener("click", loadSample);


// Stage 21 — Connect all dataset sample buttons

sampleBtn.addEventListener("click", () => {
    loadSample("any");
});

normalSampleBtn.addEventListener("click", () => {
    loadSample("normal");
});

failureSampleBtn.addEventListener("click", () => {
    loadSample("failure");
});


// Reset the prediction result when the form is reset
form.addEventListener("reset", () => {
    resultPanel.hidden = true;
    showMessage("");
});

// AI Engineering — Send machine readings to the trained model
form.addEventListener("submit", async (event) => {
    event.preventDefault();

    // Collect the values entered in the form
    const payload = {
        machine_type: document.getElementById("machine_type").value,
        air_temperature: Number(
            document.getElementById("air_temperature").value
        ),
        process_temperature: Number(
            document.getElementById("process_temperature").value
        ),
        rotational_speed: Number(
            document.getElementById("rotational_speed").value
        ),
        torque: Number(
            document.getElementById("torque").value
        ),
        tool_wear: Number(
            document.getElementById("tool_wear").value
        )
    };

    // Validate that every numeric field contains a valid number
    const numericFields = [
        "air_temperature",
        "process_temperature",
        "rotational_speed",
        "torque",
        "tool_wear"
    ];

    const invalidInput = numericFields.some(field => {
        const input = document.getElementById(field);

        return input.value.trim() === "" ||
            !Number.isFinite(payload[field]);
    });

    if (invalidInput) {
        showMessage("Please enter valid values in all fields.", "error");
        return;
    }

    // Prevent repeated submissions while prediction is running
    predictBtn.disabled = true;
    predictBtn.textContent = "Predicting...";
    resultPanel.hidden = true;

    showMessage("Sending machine readings to the AI model...");

    try {
        // Send sensor values to the FastAPI prediction endpoint
        const response = await fetch(`${API_URL}/predict`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                JSON.stringify(data.detail || data)
            );
        }

        // Display the predicted machine status
        document.getElementById("resultTitle").textContent =
            data.failure_prediction === 1
                ? "Failure Risk Detected"
                : "No Failure Predicted";

        document.getElementById("resultDescription").textContent =
            "The AI model has processed the supplied machine readings.";

        document.getElementById("predictionValue").textContent =
            data.failure_prediction === 1
                ? "Failure (1)"
                : "Normal (0)";

        document.getElementById("probabilityValue").textContent =
            (data.failure_probability * 100).toFixed(2) + "%";

        // Show the completed prediction
        resultPanel.hidden = false;

        showMessage(
            "Prediction completed successfully.",
            "success"
        );

    } catch (error) {
        showMessage(
            "Could not obtain prediction. " + error.message +
            " Check that the backend is running and CORS is configured.",
            "error"
        );

    } finally {
        predictBtn.disabled = false;
        predictBtn.textContent = "Predict Machine Failure";
    }
});

// Check API status when the dashboard first opens
checkApi();
