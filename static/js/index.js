
let timer;
let isRunning = false;
let hours = 0;
let minutes = 0;
let seconds = 0;
let milliseconds = 0;


function printRes() {
    let timerData = document.getElementById('timer').innerHTML;
    if (timerData.length == 5) {
        timerData = '00:00:' + timerData
    }
    if (timerData.length == 8) {
        timerData = '00:' + timerData
    }
    
    // Виконуємо AJAX-запит для передачі даних на сервер
    axios.post('/send_timer_data', {
        timerData: timerData
    })
    .then((response) => {
        console.log(response['data']);
        let difference = response['data']['difference'];
        if (difference[0] == '-') {
            document.getElementById('difference').style.color = "#09dd09";
        } else {
            document.getElementById('difference').style.color = "red";
        }
        document.getElementById('difference').innerHTML = difference;

        let scrambleArray = response['data']['scramble_arr'];
        document.getElementById('scramble').innerHTML = scrambleArray.join(' ');

        let bestTime = response['data']['best_time'];
        document.getElementById('best-time').innerHTML = bestTime;

        let fullAverageTime = response['data']['full_average_time'];
        document.getElementById('full-average-time').innerHTML = fullAverageTime;

        let averageLast5 = response['data']['average_last_5'];
        document.getElementById('average-time-5').innerHTML = averageLast5;

        let averageLast10 = response['data']['average_last_10'];
        document.getElementById('average-time-10').innerHTML = averageLast10;

        let data = response['data']['times'].reverse();
        let formattedData = data.join('<br>');
        document.getElementById('results').innerHTML = formattedData;
    })
    .catch(function (error) {
        console.log(error);
    });
}

function deleteLast() {
    let countDelete = prompt('Enter the number of attempts to delete:', 1)
    axios.post('/delete_attempt', {
        countDelete : countDelete
    })
    .then ((response) => {
        console.log(response)
        location.reload()
    })
    .catch ((error) => {
        console.log(error)
    })
}



function startStop() {
    if (isRunning) {
        printRes()
        clearInterval(timer);
        isRunning = false;
        document.getElementById('startStop').innerHTML = 'start';
    } else {
        reset()
        isRunning = true;
        document.getElementById('startStop').innerHTML = 'stop';
        timer = setInterval(updateTime, 10);
    }
}


function pad(num) {
    return (num < 10 ? '0' : '') + num;
}

function updateTime() {
    milliseconds++;
    if (milliseconds == 100) {
        milliseconds = 0;
        seconds++;
        if (seconds == 60) {
            seconds = 0;
            minutes++;
            if (minutes == 60) {
                minutes = 0;
                hours++;
            }
        }
    }

    let timeString = pad(seconds) + ':' + pad(milliseconds);
    if (minutes > 0) {
        timeString = pad(minutes) + ':' + timeString
    }
    if (hours > 0) {
        timeString = pad(hours) + ':' + timeString
    }

    document.getElementById('timer').innerHTML = timeString;
}

function reset() {
    milliseconds = 0;
    seconds = 0;
    minutes = 0;
    hours = 0;
    clearInterval(timer);
    document.getElementById('startStop').innerHTML = 'start';
    document.getElementById('timer').innerHTML = '00:00';
    isRunning = false;
}



document.body.onkeydown = function(e) {
    if (e.key === " ") {
        document.getElementById('timer').style.color = "red";

    }
};

document.body.onkeyup = function(e) {
    if (e.key === " ") {
        document.getElementById('timer').style.color = "white";
        startStop()
    }
};


