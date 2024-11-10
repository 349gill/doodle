let calendar = new FullCalendar.Calendar(document.getElementById('calendar'), {
    initialView: 'timeGridWeek',
    events: [],
    headerToolbar: {
        left: 'prev,next today',
        center: 'title',
        right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    eventClick: function(info) {
        openTaskPopup(info.event);
    }
});

calendar.render();

let selectedDate = null;
let currentEvent = null;

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

function closeTaskPopup() {
    document.querySelector('.task-popup').style.display = 'none';
    document.querySelector('.popup-overlay').style.display = 'none';
    currentEvent = null; // Reset current event
}

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



// static/scripts/calendar.js
document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    let currentTaskId = null;

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        eventClick: function(info) {
            showTaskPopup(info.event);
        },
        events: '/api/tasks'
    });

    calendar.render();

    // Function to show the task popup
    window.addTaskButton = function() {
        currentTaskId = null;
        document.querySelector('.task-popup h3').textContent = 'Add Task';
        document.querySelector('.remove-btn').style.display = 'none';
        document.getElementById('task-name').value = '';
        document.getElementById('task-deadline').value = '';
        document.getElementById('task-priority').value = '';
        document.getElementById('task-duration').value = '';
        document.getElementById('task-details').value = '';
        showPopup();
    }

    function showTaskPopup(event) {
        currentTaskId = event.id;
        document.querySelector('.task-popup h3').textContent = 'Edit Task';
        document.querySelector('.remove-btn').style.display = 'block';
        document.getElementById('task-name').value = event.title;
        document.getElementById('task-deadline').value = event.start.toISOString().slice(0, 16);
        document.getElementById('task-priority').value = event.extendedProps.priority;
        document.getElementById('task-duration').value = event.extendedProps.duration;
        document.getElementById('task-details').value = event.extendedProps.details;
        showPopup();
    }

    function showPopup() {
        document.querySelector('.popup-overlay').style.display = 'block';
        document.querySelector('.task-popup').style.display = 'block';
    }

    window.closeTaskPopup = function() {
        document.querySelector('.popup-overlay').style.display = 'none';
        document.querySelector('.task-popup').style.display = 'none';
    }

    window.saveTask = async function() {
        const taskData = {
            name: document.getElementById('task-name').value,
            deadline: document.getElementById('task-deadline').value,
            priority: parseInt(document.getElementById('task-priority').value),
            duration: parseFloat(document.getElementById('task-duration').value),
            details: document.getElementById('task-details').value
        };

        try {
            const response = await fetch('/api/tasks', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(taskData)
            });

            if (response.ok) {
                const newTask = await response.json();
                calendar.refetchEvents();
                closeTaskPopup();
            } else {
                alert('Failed to save task');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error saving task');
        }
    }

    window.removeTask = async function() {
        if (!currentTaskId) return;

        try {
            const response = await fetch(`/api/tasks/${currentTaskId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                calendar.refetchEvents();
                closeTaskPopup();
            } else {
                alert('Failed to delete task');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error deleting task');
        }
    }
});


