
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.4.0/firebase-app.js";

import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  sendPasswordResetEmail,
  updateProfile
} from "https://www.gstatic.com/firebasejs/12.4.0/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyBz2OqICHFUawp6qNUAa_5zuScb1GtVRM4",
  authDomain: "studdybuddy-5d8b3.firebaseapp.com",
  projectId: "studdybuddy-5d8b3",
  storageBucket: "studdybuddy-5d8b3.firebasestorage.app",
  messagingSenderId: "872929940201",
  appId: "1:872929940201:web:9ecaaae5e1640226ca9678",
  measurementId: "G-G8XG2HG8VP"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Redirect to your Flask materials page after login/signup.
const HOME_PAGE = "/materials";

// HTML elements
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
const forgotBtn = document.getElementById("forgotBtn");
const forgotRow = document.getElementById("forgotRow");
const switchText = document.getElementById("switchText");
const switchBtn = document.getElementById("switchBtn");

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

function friendlyError(error) {
  const messages = {
    "auth/email-already-in-use":
      "This email already has an account. Try logging in.",
    "auth/invalid-email":
      "Please enter a valid email address.",
    "auth/weak-password":
      "Choose a stronger password with at least 6 characters.",
    "auth/invalid-credential":
      "Email or password is incorrect. Check your details.",
    "auth/user-not-found":
      "No account found. Please sign up first.",
    "auth/wrong-password":
      "Incorrect password. Try again.",
    "auth/too-many-requests":
      "Too many attempts. Please wait and try again.",
    "auth/network-request-failed":
      "Network error. Check your internet connection."
  };

  return messages[error.code] ||
    "Something went wrong. Please try again.";
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  showMessage("");

  const email = emailInput.value.trim();
  const password = passwordInput.value;

  submitBtn.disabled = true;
  submitBtn.textContent = mode === "signup"
    ? "Creating account..."
    : "Logging in...";

  try {
    if (mode === "signup") {
      const name = nameInput.value.trim();

      if (!name) {
        showMessage("Please enter your name.");
        return;
      }

      const credential = await createUserWithEmailAndPassword(
        auth, email, password
      );

      await updateProfile(credential.user, {
        displayName: name
      });
    } else {
      await signInWithEmailAndPassword(auth, email, password);
    }

    // Redirect after Firebase confirms authentication.
    window.location.replace(HOME_PAGE);

  } catch (error) {
    showMessage(friendlyError(error));
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = mode === "signup"
      ? 'Create account <span>→</span>'
      : 'Log in <span>→</span>';
  }
});

forgotBtn.addEventListener("click", async () => {
  const email = emailInput.value.trim();

  if (!email) {
    showMessage("Enter your email address first.");
    emailInput.focus();
    return;
  }

  try {
    await sendPasswordResetEmail(auth, email);

    showMessage(
      "If an account exists for this address, a reset email will be sent.",
      "success"
    );
  } catch (error) {
    if (error.code === "auth/invalid-email") {
      showMessage("Please enter a valid email address.");
    } else {
      showMessage("Unable to send the reset email. Please try again.");
    }
  }
});
