// ===============================
// Daily Goal
// ===============================

const DAILY_GOAL = 10;

// ===============================
// Get Study Sessions
// ===============================

let sessions = Number(localStorage.getItem("studySessions")) || 0;

// Display Session Count
document.getElementById("sessionCount").textContent = sessions;

// ===============================
// Progress Bar
// ===============================

let percent = (sessions / DAILY_GOAL) * 100;

if (percent > 100) {
    percent = 100;
}

const fill = document.getElementById("progressFill");
const text = document.getElementById("progressText");

// Animate after page loads
setTimeout(() => {

    fill.style.width = percent + "%";
    text.textContent = Math.round(percent) + "% Completed";

}, 400);

// ===============================
// Save Checklist
// ===============================

const checkboxes = document.querySelectorAll("input[type='checkbox']");

// Restore saved state
checkboxes.forEach((checkbox, index) => {

    const saved = localStorage.getItem("task" + index);

    if (saved === "true") {
        checkbox.checked = true;
    }

    checkbox.addEventListener("change", () => {

        localStorage.setItem("task" + index, checkbox.checked);

    });

});

// ===============================
// Achievement Message
// ===============================

if (sessions >= DAILY_GOAL) {

    setTimeout(() => {

        alert("🏆 Congratulations! You reached today's study goal!");

    }, 700);

}

// ===============================
// Motivational Quotes
// ===============================

const quotes = [

    "Success is the sum of small efforts repeated every day. 💜",

    "Stay focused and never stop learning. 📚",

    "Every study session brings you closer to your goal. 🚀",

    "Consistency beats motivation. ⭐",

    "Dream big. Study smart. Achieve more. 🎯"

];

// Create quote card dynamically
const quoteCard = document.createElement("div");

quoteCard.className = "card";

quoteCard.innerHTML = `
    <h2>💡 Motivation</h2>
    <p style="margin-top:20px; line-height:1.8;">
        "${quotes[Math.floor(Math.random() * quotes.length)]}"
    </p>
`;

document.querySelector(".container").appendChild(quoteCard);
// ===============================
// Dashboard Statistics
// ===============================

let totalHours = Number(localStorage.getItem("totalHours")) || (sessions * 0.5);
let streak = Number(localStorage.getItem("studyStreak")) || 7;
let goals = Number(localStorage.getItem("goalsCompleted")) || Math.floor(sessions / DAILY_GOAL);

document.getElementById("totalHours").textContent = totalHours;
document.getElementById("streak").textContent = streak;
document.getElementById("sessions").textContent = sessions;
document.getElementById("goals").textContent = goals;
new Chart(document.getElementById("lineChart"), {

    type: "line",

    data: {
        labels: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],

        datasets: [{
            label: "Study Hours",

            data: [2,3,4,2,5,6,totalHours],

            borderColor: "#8B5CF6",

            backgroundColor: "rgba(168,85,247,.2)",

            fill: true,

            tension: .4
        }]
    }

});
new Chart(document.getElementById("barChart"),{

type:"bar",

data:{

labels:["Math","Science","English","Programming","History"],

datasets:[{

label:"Hours",

data:[12,8,6,15,4],

backgroundColor:[
"#C084FC",
"#A855F7",
"#8B5CF6",
"#7C3AED",
"#DDD6FE"
]

}]

}

});
new Chart(document.getElementById("pieChart"),{

type:"pie",

data:{

labels:["Math","Science","English","Programming","History"],

datasets:[{

data:[30,20,15,25,10],

backgroundColor:[
"#C084FC",
"#A855F7",
"#8B5CF6",
"#DDD6FE",
"#E9D5FF"
]

}]

}

});
new Chart(document.getElementById("weekChart"),{

type:"bar",

data:{

labels:["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],

datasets:[{

label:"Study Sessions",

data:[2,4,3,5,6,4,sessions],

backgroundColor:"#A855F7"

}]

},

options:{

scales:{

y:{
beginAtZero:true
}

}

}

});
// Unlock achievements

if(totalHours >= 10){

document.querySelectorAll(".achievement")[0].classList.remove("locked");
document.querySelectorAll(".achievement")[0].classList.add("unlocked");

}

if(streak >= 7){

document.querySelectorAll(".achievement")[1].classList.remove("locked");
document.querySelectorAll(".achievement")[1].classList.add("unlocked");

}

if(sessions >= 50){

document.querySelectorAll(".achievement")[2].classList.remove("locked");
document.querySelectorAll(".achievement")[2].classList.add("unlocked");

}