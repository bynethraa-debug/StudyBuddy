
const form = document.getElementById("authForm");
const loginTab = document.getElementById("loginTab");
const signupTab = document.getElementById("signupTab");
const nameField = document.getElementById("nameField");
const nameInput = document.getElementById("name");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const title = document.getElementById("formTitle");
const subtitle = document.getElementById("formSubtitle");
const submitBtn = document.getElementById("submitBtn");
const message = document.getElementById("message");
const forgotRow = document.getElementById("forgotRow");
const switchText = document.getElementById("switchText");
const switchBtn = document.getElementById("switchBtn");
const forgotBtn = document.getElementById("forgotBtn");

let mode = "login";

function showMessage(text, type = "error") {
    message.textContent = text;
    message.className = `message ${type}`;
}

function setMode(nextMode) {
    mode = nextMode;
    const isSignup = mode === "signup";

    loginTab.classList.toggle("active", !isSignup);
    signupTab.classList.toggle("active", isSignup);

    nameField.hidden = !isSignup;
    nameInput.required = isSignup;
    forgotRow.hidden = isSignup;

    passwordInput.autocomplete = isSignup
        ? "new-password"
        : "current-password";

    title.textContent = isSignup
        ? "Create your account"
        : "Welcome back!";

    subtitle.textContent = isSignup
        ? "Start building your study routine today."
        : "Log in to continue your learning journey.";

    submitBtn.innerHTML = isSignup
        ? 'Create account <span>→</span>'
        : 'Log in <span>→</span>';

    switchText.firstChild.textContent = isSignup
        ? "Already have an account? "
        : "New to StudyBuddy? ";

    switchBtn.textContent = isSignup
        ? "Log in"
        : "Create an account";

    showMessage("");
}

loginTab.addEventListener("click", () => setMode("login"));
signupTab.addEventListener("click", () => setMode("signup"));

switchBtn.addEventListener("click", () => {
    setMode(mode === "login" ? "signup" : "login");
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    showMessage("");

    const currentMode = mode;
    const name = nameInput.value.trim();
    const email = emailInput.value.trim().toLowerCase();
    const password = passwordInput.value;

    if (currentMode === "signup" && !name) {
        showMessage("Please enter your name.");
        return;
    }

    if (!email || !password) {
        showMessage("Please fill in all required fields.");
        return;
    }

    if (currentMode === "signup" && password.length < 8) {
        showMessage("Password must be at least 8 characters.");
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = currentMode === "signup"
        ? "Creating account..."
        : "Logging in...";

    try {
        const endpoint = currentMode === "signup"
            ? "/auth/register"
            : "/auth/login";

        const response = await fetch(endpoint, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(data.error || "Something went wrong.");
            return;
        }

        showMessage(
            currentMode === "signup"
                ? "Account created successfully!"
                : "Login successful!",
            "success"
        );

        window.location.href = "/materials";

    } catch (error) {
        console.error("Authentication error:", error);
        showMessage("Could not connect to StudyBuddy. Please try again.");
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = mode === "signup"
            ? 'Create account <span>→</span>'
            : 'Log in <span>→</span>';
    }
});

forgotBtn.addEventListener("click", () => {
    showMessage(
        "Password recovery is not set up yet. Please contact the site administrator."
    );
});

setMode("login");

