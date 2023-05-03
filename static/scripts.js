$(document).ready(function () {
    $("#setup_form").on("submit", function (event) {
        event.preventDefault();
        const formData = $(this).serialize(); // Serialize the form data before disabling the fields
        toggleFormFields(true); // Disable the form fields
        $.ajax({
            url: "/setup",
            method: "POST",
            data: formData,
            success: function (response) {
                if (response.status === "success") {
                    // Display success alert
                    $("#message").html('<div class="alert alert-success" role="alert">' + response.message + '</div>');
                    // Redirect to chat page
                    window.location.href = "/chat";
                } else {
                    $("#message").html('<div class="alert alert-danger" role="alert">' + response.message + '</div>');
                    toggleFormFields(false); // Enable the form fields
                }
            },
            error: function () {
                $("#message").html('<div class="alert alert-danger" role="alert">An error occurred while processing the request.</div>');
                toggleFormFields(false); // Enable the form fields
            }
        });
    });

    $("#send_button").on("click", function () {
        var userMessage = $("#user_message").val().trim();
        if (userMessage !== "") {
            $("#user_message").val("");
            $("#chatlog").append('<div class="user-message">You: ' + escapeHtml(userMessage) + '</div>');
            scrollToBottom(); // Scroll to the bottom after appending user message
            $.ajax({
                url: "/send_message", // Change this line to use the correct endpoint
                method: "POST",
                data: { message: userMessage },
                success: function (response) {
                    if (response.status === "success") {
                        if (response.message) {
                            $("#chatlog").append('<div class="assistant-message">ChatGPT: ' + escapeHtml(response.message) + '</div>');
                        } else {
                            $("#chatlog").append('<div class="error-message">Error: Received an empty response.</div>');
                        }
                        scrollToBottom(); // Scroll to the bottom after appending assistant message
                    } else {
                        if (response.message) {
                            $("#chatlog").append('<div class="error-message">Error: ' + escapeHtml(response.message) + '</div>');
                        } else {
                            $("#chatlog").append('<div class="error-message">Error: An unknown error occurred.</div>');
                        }
                        scrollToBottom(); // Scroll to the bottom after appending error message
                    }
                }
            });
        }
    });

    $("#user_message").on("keypress", function (event) {
        if (event.which == 13 && !event.shiftKey) {
            event.preventDefault();
            $("#send_button").click();
        }
    });
});

function toggleFormFields(disable) {
    $("#setup_form input, #setup_form select, #setup_form button").prop("disabled", disable);
}

function escapeHtml(text) {
    return text
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/(?:\r\n|\r|\n)/g, '<br>') // Replace newline characters with <br>
        .replace(/\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;') // Replace tab characters with four non-breaking spaces
        .replace(/  +/g, function (match) {
            return match.split('').map(() => '&nbsp;').join('');
        }); // Replace consecutive spaces with non-breaking spaces
}

function scrollToBottom() {
    const chatlog = document.getElementById("chatlog");
    chatlog.scrollTop = chatlog.scrollHeight;
}
