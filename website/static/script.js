document.getElementById("form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = {
        user_id: user_id,
        age: age.value,
        heartRate: heartRate.value,
        restingHR: restingHR.value,
        systolic: systolic.value,
        diastolic: diastolic.value
    };

    const res = await fetch("/predict", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(data)
    });

    const result = await res.json();

    document.getElementById("result").innerHTML =
        `Final Risk: ${result.finalRisk} | Reason: ${result.reason}`;
});

async function loadHistory() {
    const res = await fetch(`/history/${user_id}`);
    const data = await res.json();

    document.getElementById("history").innerText =
        JSON.stringify(data, null, 2);
}