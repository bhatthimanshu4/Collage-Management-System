// ✅ Toastify Function (Globally Define Karo)
function showToast(message, color = "green") {
    Toastify({
        text: message,
        duration: 3000,
        gravity: "top",
        position: "center",
        backgroundColor: color,
        stopOnFocus: true,
    }).showToast();
}

// ✅ Update Student Function
function updateStudentData() {
    let studentId = document.getElementById("student_id").value.trim();

    if (!studentId) {
        showToast("❌ Please enter a valid Student ID!", "red");
        return;
    }

    console.log(`📤 Sending Update Request to: http://127.0.0.1:5000/update_student/${studentId}`);

    fetch(`http://127.0.0.1:5000/update_student/${studentId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            name: document.getElementById("name").value,
            father_name: document.getElementById("father_name").value,
            mother_name: document.getElementById("mother_name").value,
            address: document.getElementById("address").value,
            mobileno: document.getElementById("mobileno").value,
            email_address: document.getElementById("email_address").value,
            date_of_birth: document.getElementById("date_of_birth").value,
            gender: document.getElementById("gender").value
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast("✅ Student updated successfully!", "green");

            // ✅ Redirect after Toast completes (3 sec delay)
            setTimeout(() => {
                window.location.href = "check_Std_info.html"; 
            }, 3000);

        } else {
            showToast("❌ Update failed: " + data.message, "red");
        }
    })
    .catch(error => {
        console.error("❌ Error in updateStudentData():", error);
        showToast("❌ Error updating student!", "red");
    });
}
