// Initialize the calendar
let calendar = new FullCalendar.Calendar(document.getElementById('calendar'), {
    initialView: 'dayGridMonth',
    events: [],
    headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    eventClick: function(info) {
        // When event is clicked, open the task popup with event details
        openTaskPopup(info.event);
    }
});

calendar.render();

// Store the selected date
let selectedDate = null;
let currentEvent = null;  // To store the event being edited or deleted

// Open the task popup with pre-filled event data if editing an existing event
function openTaskPopup(event = null) {
    document.querySelector('.task-popup').style.display = 'block';
    document.querySelector('.popup-overlay').style.display = 'block';

    if (event) {
        // Editing existing event
        currentEvent = event;
        document.getElementById('task-name').value = event.title;
        document.getElementById('task-deadline').value = moment(event.start).format('YYYY-MM-DDTHH:mm');
        document.getElementById('task-priority').value = event.extendedProps.priority;
        document.getElementById('task-duration').value = event.extendedProps.duration;
        document.getElementById('task-details').value = event.extendedProps.description;

        // Show the "Delete Task" button
        document.querySelector('.remove-btn').style.display = 'block';
    } else {
        // Adding a new task (no event selected)
        currentEvent = null;
        document.getElementById('task-name').value = '';
        document.getElementById('task-deadline').value = '';
        document.getElementById('task-priority').value = '';
        document.getElementById('task-duration').value = '';
        document.getElementById('task-details').value = '';

        // Hide the "Delete Task" button
        document.querySelector('.remove-btn').style.display = 'none';
    }
}

// Close the task popup
function closeTaskPopup() {
    document.querySelector('.task-popup').style.display = 'none';
    document.querySelector('.popup-overlay').style.display = 'none';
    currentEvent = null; // Reset current event
}

// Save the task and add it to the calendar
function saveTask() {
    const name = document.getElementById('task-name').value;
    const deadline = document.getElementById('task-deadline').value;
    const priority = document.getElementById('task-priority').value;
    const duration = document.getElementById('task-duration').value;
    const details = document.getElementById('task-details').value;

    if (name && deadline && priority && duration) {
        if (currentEvent) {
            // Update existing event
            currentEvent.setProp('title', name);
            currentEvent.setStart(deadline);
            currentEvent.setExtendedProp('priority', priority);
            currentEvent.setExtendedProp('duration', duration);
            currentEvent.setExtendedProp('description', details);
        } else {
            // Add a new event
            calendar.addEvent({
                title: name,
                start: deadline,
                description: details,
                extendedProps: {
                    priority: priority,
                    duration: duration
                },
                color: '#0066FF'
            });
        }

        closeTaskPopup();
    } else {
        alert("Please fill in all fields.");
    }
}

// Delete the selected task
function removeTask() {
    if (currentEvent) {
        currentEvent.remove();
        closeTaskPopup();
    }
}

// Function to trigger Add Task
function addTaskButton() {
    openTaskPopup();
}
