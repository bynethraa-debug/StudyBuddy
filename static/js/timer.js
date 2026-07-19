// =========================
// POMODORO SETTINGS
// =========================

let studyMinutes = 25;
let shortBreak = 5;
let longBreak = 15;

let totalPomodoros = 4;
let currentPomodoro = 1;

let mode = "study";

let timeLeft = studyMinutes * 60;

let timer = null;
let running = false;

// =========================
// ELEMENTS
// =========================

const timerDisplay = document.getElementById("timer");

const startBtn = document.getElementById("startBtn");
const pauseBtn = document.getElementById("pauseBtn");
const resetBtn = document.getElementById("resetBtn");
const subjectSelect = document.getElementById("subjectSelect");

const taskInput = document.getElementById("taskInput");

const historyContainer =
document.getElementById("sessionHistory");

const pomodoroCounter = document.querySelector(".pomodoro-count");
const pomodoroBtn = document.getElementById("pomodoroBtn");
const shortBreakBtn = document.getElementById("shortBreakBtn");
const longBreakBtn = document.getElementById("longBreakBtn");

// =========================
// DISPLAY
// =========================

function updateDisplay(){

    let minutes = Math.floor(timeLeft / 60);

    let seconds = timeLeft % 60;

    timerDisplay.textContent =
        `${String(minutes).padStart(2,"0")}:${String(seconds).padStart(2,"0")}`;

}

updateDisplay();

// =========================
// START
// =========================

startBtn.onclick = () => {

    if(running) return;

    running = true;

    timer = setInterval(countdown,1000);

};

// =========================
// PAUSE
// =========================

pauseBtn.onclick = () => {

    clearInterval(timer);

    running = false;

};

// =========================
// RESET
// =========================

resetBtn.onclick = () => {

    clearInterval(timer);

    running = false;

    if(mode==="study"){
        saveSession();

        timeLeft = studyMinutes*60;

    }else if(mode==="short"){

        timeLeft = shortBreak*60;

    }else{

        timeLeft = longBreak*60;

    }

    updateDisplay();

};

// =========================
// COUNTDOWN
// =========================
function setMode(newMode){

    clearInterval(timer);

    running = false;

    mode = newMode;

    if(mode==="study"){

        timeLeft = studyMinutes * 60;

    }

    else if(mode==="short"){

        timeLeft = shortBreak * 60;

    }

    else{

        timeLeft = longBreak * 60;

    }

    updateDisplay();

    pomodoroBtn.classList.remove("active");
    shortBreakBtn.classList.remove("active");
    longBreakBtn.classList.remove("active");

    if(mode==="study")
        pomodoroBtn.classList.add("active");

    if(mode==="short")
        shortBreakBtn.classList.add("active");

    if(mode==="long")
        longBreakBtn.classList.add("active");

}
function countdown(){

    if(timeLeft>0){

        timeLeft--;

        updateDisplay();

        return;

    }

    clearInterval(timer);

    running=false;

    switchMode();

}

// =========================
// SWITCH MODES
// =========================

function switchMode(){

    if(mode==="study"){
        saveSession();

        if(currentPomodoro===totalPomodoros){

            mode="long";

            timeLeft=longBreak*60;

            alert("🎉 Great job! Time for a long break.");

            currentPomodoro=1;

        }else{

            mode="short";

            timeLeft=shortBreak*60;

            alert("☕ Time for a short break!");

        }

    }

    else if(mode==="short"){

        mode="study";

        currentPomodoro++;

        timeLeft=studyMinutes*60;

    }

    else{

        mode="study";

        timeLeft=studyMinutes*60;

    }

    pomodoroCounter.innerHTML =
        `🌿 Pomodoro ${currentPomodoro} / ${totalPomodoros}`;

    updateDisplay();

}
function saveSession(){

    const sessions =
    JSON.parse(localStorage.getItem("sessions")) || [];

    sessions.unshift({

        subject:
        subjectSelect.value,

        task:
        taskInput.value || "Untitled Task",

        duration:
        studyMinutes,

        completedAt:
        new Date().toLocaleString()

    });

    localStorage.setItem(
        "sessions",
        JSON.stringify(sessions)
    );

    loadSessions();

    updateStats();
    pomodoroBtn.onclick = () => {

    setMode("study");

};

shortBreakBtn.onclick = () => {

    setMode("short");

};

longBreakBtn.onclick = () => {

    setMode("long");

};

}


function loadSessions(){

    const sessions =
    JSON.parse(localStorage.getItem("sessions")) || [];

    historyContainer.innerHTML="";

    sessions.slice(0,5).forEach(session=>{

        historyContainer.innerHTML+=`

        <div class="session">

            <div>

                <strong>${session.subject}</strong>

                <p>${session.task}</p>

            </div>

            <span>${session.duration} min</span>

        </div>

        `;

    });

}
function updateStats(){

    const sessions =
    JSON.parse(localStorage.getItem("sessions")) || [];

    document.getElementById("pomodoroCount")
        .textContent = sessions.length;

    const minutes =
    sessions.reduce(
        (sum,s)=>sum+s.duration,
        0
    );

    document.getElementById("focusTime")
        .textContent =
        minutes+" min";

    const uniqueTasks =
    [...new Set(
        sessions.map(s=>s.task)
    )];

    document.getElementById("taskCount")
        .textContent =
        uniqueTasks.length;

}
loadSessions();

updateStats();