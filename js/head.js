// Function to handle clicks on elements
function toggleClassOnClick(element) {
    if (!element.dataset.listener) {
        element.addEventListener('click', function (event) {
            event.stopPropagation() // Stop event bubbling
            event.preventDefault() // Prevent default behavior

            // Toggle the 'deleted' class
            element.classList.toggle('deleted')

            // Apply styles
            element.style.backgroundColor = element.classList.contains('deleted') ? 'red' : ''
        })

        element.dataset.listener = 'true' // Mark that the listener has been added
    }
}

class Slider {
    constructor(element, options = {}) {
        this.element = element
        this.min = options.min || 0
        this.max = options.max || 100
        this.value = options.value || this.min
        this.step = options.step || 1
        this.init()
    }

    init() {
        this.sliderContainer = document.createElement('div')
        this.sliderContainer.className = 'slider'

        this.input = document.createElement('input')
        this.input.type = 'range'
        this.input.min = this.min
        this.input.max = this.max
        this.input.value = this.value
        this.input.step = this.step

        this.hiddenInput = document.createElement('input')
        this.hiddenInput.type = 'hidden'
        this.hiddenInput.value = this.value

        this.input.addEventListener('input', (e) => this.handleChange(e))

        this.sliderValue = document.createElement('div')
        this.sliderValue.className = 'slider-value'

        this.sliderContainer.appendChild(this.input)
        this.sliderContainer.appendChild(this.hiddenInput)
        this.sliderContainer.appendChild(this.sliderValue)

        this.element.appendChild(this.sliderContainer)

        this.renderNumbers()
        this.updateBackground()
    }

    handleChange(e) {
        this.value = e.target.value
        this.hiddenInput.value = this.value
        this.updateNumbers()
        this.updateBackground()
    }

    percent() {
        return ((this.value - this.min) * 100) / (this.max - this.min)
    }

    renderNumbers() {
        const length = this.max.toString().length
        for (let i = 0; i < length; i++) {
            const numberContainer = document.createElement('div')
            numberContainer.className = 'slider-value-number'

            const ul = document.createElement('ul')
            for (let j = 0; j < 10; j++) {
                const li = document.createElement('li')
                li.textContent = j
                ul.appendChild(li)
            }

            numberContainer.appendChild(ul)
            this.sliderValue.appendChild(numberContainer)
        }
        this.updateNumbers()
    }

    updateNumbers() {
        const valueStr = this.value.toString().padStart(this.max.toString().length, '0') // Ensure the string length is consistent with `max`
        const length = this.max.toString().length

        Array.from(this.sliderValue.children).forEach((numberContainer, index) => {
            const charIndex = index - (length - valueStr.length)
            const isVisible = charIndex >= 0
            const digit = isVisible ? valueStr[charIndex] : '0'
            const position = isVisible ? `-${parseInt(digit) * 10}%` : '10%'

            const ul = numberContainer.querySelector('ul')
            ul.style.transform = `translateY(${position})`
            ul.style.opacity = isVisible ? '1' : '0'
        })
    }

    updateBackground() {
        this.input.style.backgroundSize = `${this.percent()}% 100%`
    }
}

// Updated function to initialize handlers
const initializeObservers = (target) => {
    // Initialize sliders
    initializeSliders(target, 'div.subject-info > div.info > div.range > div.subject_relevance')
    initializeSliders(target, 'div.add-range > div.range > div.slider-container')

    // Add click handlers for skill elements
    target
        .querySelectorAll('div.subject-info > div.info > div.info-skills > span.value > span.skill')
        .forEach((element) => toggleClassOnClick(element))
}

/**
 * Initializes sliders for the provided elements if they have not been initialized.
 * @param {Element} target - Element inside which sliders should be initialized.
 * @param {string} selector - Selector used to find slider elements.
 */
const initializeSliders = (target, selector) => {
    target.querySelectorAll(selector).forEach((element) => {
        if (!element.classList.contains('initialized')) {
            new Slider(element, { min: 1, max: 7, value: 4 })
            element.classList.add('initialized')
        }
    })
}

const NO_DATA = 'Нет данных'
const NOT_SPECIFIED = 'не указан'

/**
 * Extracts data from input fields with the ancestor classes .user-info and .dropdown-user.
 * @param {string} containerSelector - Selector for the container with user data.
 * @returns {Object} Object containing the input field data.
 */
function extractUserInputData(containerSelector) {
    const userContainer = document.querySelector(containerSelector)

    if (!userContainer) {
        console.error('Элемент контейнера пользователя не найден')
        return { error: 'Container not found' }
    }

    // Extract field values
    const userInfoLabels = userContainer.querySelectorAll('span[data-testid="block-info"]')
    const userInfoInputs = userContainer.querySelectorAll('.user-info input')
    const dropdownUserInput = userContainer.querySelector('.dropdown-user input')

    const userData = {
        [userInfoLabels[0]?.textContent.trim() || NO_DATA]: userInfoInputs[0]?.value || NO_DATA, // First input
        [userInfoLabels[1]?.textContent.trim() || NO_DATA]: userInfoInputs[1]?.value || NO_DATA, // Second input
        [userInfoLabels[2]?.textContent.trim() || NO_DATA]: dropdownUserInput?.value || NO_DATA, // Third input
    }

    return userData
}

/**
 * Extracts skills from the provided container.
 * @param {Element} container - DOM element containing skills.
 * @param {string} skillsSelector - Selector for skills.
 * @returns {Object} Object with relevant and removed skills.
 */
function extractSkills(container, skillsSelector) {
    let skillsLabel = container.querySelector(`${skillsSelector} .label`)?.textContent.trim() || NO_DATA

    // Remove a trailing colon if present
    skillsLabel = skillsLabel.replace(/:$/, '')

    // Extract all skills
    const allSkills = [...container.querySelectorAll(`${skillsSelector} .value .skill`)].map((skill) =>
        skill.textContent.trim(),
    )

    // Extract skills marked as removed
    const deletedSkills = [...container.querySelectorAll(`${skillsSelector} .value .skill.deleted`)].map((skill) =>
        skill.textContent.trim(),
    )

    // Filter relevant skills
    const deletedSkillsSet = new Set(deletedSkills)
    const relevantSkills = allSkills.filter((skill) => !deletedSkillsSet.has(skill))

    return {
        [`${skillsLabel} (релевантные)`]: relevantSkills,
        [`${skillsLabel} (удаленные)`]: deletedSkills,
    }
}

/**
 * Extracts course relevance data with the option to provide a custom label.
 * @param {Element} infoBlock - Block containing course information.
 * @param {string} [customLabel] - (Optional) Custom label for the range.
 * @returns {Object} Object with the course relevance data.
 */
function extractRangeData(rangeBlock, customLabel) {
    // const rangeBlock = infoBlock.querySelector('.range');

    let rangeLabel = customLabel || rangeBlock.querySelector('label')?.textContent.trim() || NO_DATA
    const rangeValue = rangeBlock.querySelector('input[type="hidden"]')?.value || NO_DATA

    // Remove a trailing colon if present
    rangeLabel = rangeLabel.replace(/:$/, '')

    return { [rangeLabel]: rangeValue }
}

/**
 * Extracts course details from the information block.
 * @param {Element} infoBlock - Block with course information.
 * @returns {Object} Object containing course details.
 */
function extractCourseData(infoBlock) {
    const infoItems = infoBlock.querySelectorAll('.info-item')
    const courseDetails = {}

    infoItems.forEach((item) => {
        let label = item.querySelector('.label')?.textContent.trim() || NO_DATA
        const value = item.querySelector('.value')?.textContent.trim() || NO_DATA

        // Remove a trailing colon if present
        label = label.replace(/:$/, '')

        courseDetails[label] = value
    })

    // Check for the training number error block
    if (infoBlock.querySelector('.info-number-education-error')) {
        courseDetails['Курс обучения'] = NOT_SPECIFIED
    }

    return courseDetails
}

/**
 * Extracts additional skills from the .dropdown-add-vacancy-skills block.
 * @param {string} containerSelector - Selector for the container with additional skills.
 * @returns {Array} Array of additional skills.
 */
function extractAdditionalSkills(containerSelector) {
    const container = document.querySelector(containerSelector)

    if (!container) {
        console.error('Элемент контейнера дополнительных навыков не найден')
        return []
    }

    // Find all elements with the 'token' class inside the container
    const tokenElements = container.querySelectorAll('.token')

    // Extract text values from the span inside each 'token' element
    const skills = [...tokenElements]
        .map((token) => {
            const skillText = token.querySelector('span')?.textContent.trim() || ''
            // Return only non-empty skills
            return skillText ? skillText : null
        })
        .filter((skill) => skill !== null) // Skip empty values

    return skills
}

function calculateTimeDifference(startTime, endTime) {
    // Calculate the difference in milliseconds
    let timeDifferenceMs = endTime - startTime

    // Break down the time into hours, minutes, seconds, and milliseconds
    const hours = Math.floor(timeDifferenceMs / (1000 * 60 * 60))
    timeDifferenceMs %= 1000 * 60 * 60 // Remaining part after subtracting hours

    const minutes = Math.floor(timeDifferenceMs / (1000 * 60))
    timeDifferenceMs %= 1000 * 60 // Remaining part after subtracting minutes

    const seconds = Math.floor(timeDifferenceMs / 1000)
    const milliseconds = timeDifferenceMs % 1000 // Remaining part after subtracting seconds

    // Return an object with the time breakdown
    return {
        hours: hours,
        minutes: minutes,
        seconds: seconds,
        milliseconds: milliseconds,
    }
}

// Function for sending data to the server
function sendDataToServer(data, showAlerts = true) {
    fetch('/api/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then((response) => {
            if (!response.ok) {
                throw new Error('Ошибка сети при отправке данных')
            }
            return response.json()
        })
        .then((responseData) => {
            if (showAlerts) {
                if (responseData.status === 'success') {
                    // Actions for successful handling
                    alert(responseData.message)
                } else if (responseData.status === 'error') {
                    // Actions when the server returns an error
                    alert('Ошибка сервера: ' + responseData.error)
                } else {
                    // Handle unexpected statuses
                    alert('Неизвестный статус ответа от сервера.')
                }
            }
        })
        .catch((error) => {
            if (showAlerts) {
                // Handle errors without logging details to the console
                alert('Не удалось отправить данные на сервер. Пожалуйста, попробуйте позже.')
            }
        })
}

/**
 * Main function for processing data when the button is clicked.
 */

function handleButtonClick(showAlerts = true) {
    const result = {
        user_id: null,
        user_data: null,
        user_message: NO_DATA,
        session_id: null,
        vacancy: null,
        edu_groups: [],
        additional_vacancy_skills: [],
        additional_subjects_skills: [],
        feedback: null,
        time: null,
    }

    // Extract user data
    result.user_id = document.querySelector('.block.user-id input')?.value.trim() || NO_DATA

    // Extract user data
    result.user_data = extractUserInputData('.user-container .form')

    // Find the user message
    result.user_message =
        document.querySelector('.chatbot-container .message.user button > span.chatbot.prose')?.textContent.trim() ||
        NO_DATA

    result.session_id = document.querySelector('.chatbot-id input')?.value.trim() || NO_DATA

    // Find the container with the bot's response
    const spanContainer = document.querySelector('.chatbot-container .message.bot button span.chatbot')

    if (!spanContainer) {
        console.error('Элемент span с классами chatbot не найден')
        return
    }

    // Extract vacancy information
    const subjectInfo = spanContainer.querySelector('.subject-info')
    if (subjectInfo && subjectInfo.parentElement === spanContainer) {
        result.vacancy = extractSkills(subjectInfo, '.info-skills')
    } else {
        console.error('Элемент .subject-info не найден')
        return
    }

    // Process education groups
    const eduGroups = spanContainer.querySelectorAll('.edu-group')

    if (eduGroups.length > 0) {
        eduGroups.forEach((eduGroup, index) => {
            const groupLabel = eduGroup.querySelector('span')?.textContent.trim() || `Группа ${index + 1}`

            // Extract courses from the current group
            const courses = [...eduGroup.querySelectorAll('.info')].map((infoBlock) => {
                const courseDetails = extractCourseData(infoBlock)
                const relevanceData = extractRangeData(infoBlock.querySelector('.range'))
                const pudSkills = extractSkills(infoBlock, '.info-skills')

                return {
                    ...courseDetails,
                    ...relevanceData,
                    ...pudSkills,
                }
            })

            result.edu_groups.push({
                label: groupLabel,
                courses: courses,
            })
        })
    } else {
        console.error('Элементы .edu-group не найдены')
    }

    // Extract additional vacancy skills
    result.additional_vacancy_skills = extractAdditionalSkills('.dropdown-add-vacancy-skills')

    // Extract additional subject skills
    result.additional_subjects_skills = extractAdditionalSkills('.dropdown-add-subjects-skills')

    // Extract data from the service evaluation block
    const addRangeContainer = document.querySelector('.block.add-range')
    if (addRangeContainer) {
        const customLabels = ['Полезность', 'Востребованность', 'Удобство']

        const ranges = [...addRangeContainer.querySelectorAll('.range')].map((rangeBlock, index) => {
            // Get a custom label for the current rangeBlock
            const customLabel = customLabels[index] || `Диапазон ${index + 1}`
            return extractRangeData(rangeBlock, customLabel)
        })

        // Combine all ranges into a single object
        result.additional_ranges = Object.assign({}, ...ranges)
    } else {
        console.error('Элемент .add-range не найден')
    }

    // Extract the user feedback from the textarea inside .block .feedback
    result.feedback = document.querySelector('.block.feedback textarea')?.value.trim() || NO_DATA

    // Calculate the time difference
    const startTimeValue = document.querySelector('div.chatbot-timer input')?.value
    if (startTimeValue) {
        // Convert the start time to seconds
        const startTime = new Date(parseFloat(startTimeValue) * 1000) // Convert to milliseconds
        const endTime = new Date()

        if (isNaN(startTime)) {
            console.error('Неверный формат начального времени:', startTimeValue)
        } else {
            // Calculate the time difference
            result.time = {
                ...calculateTimeDifference(startTime, endTime), // Breakdown into hours, minutes, seconds, and milliseconds
                start_timestamp: (startTime.getTime() / 1000).toFixed(5), // Start timestamp in seconds with milliseconds
                end_timestamp: (endTime.getTime() / 1000).toFixed(5), // End timestamp in seconds with milliseconds
                elapsed_time_ms: endTime - startTime, // Elapsed time in milliseconds
                elapsed_time_s: ((endTime - startTime) / 1000).toFixed(3), // Elapsed time in seconds
            }
        }
    } else {
        console.error('Начальное время не найдено или не задано')
    }

    // Log the final result
    console.log('Полный результат:', JSON.stringify(result, null, 2))

    // Send data to the server
    sendDataToServer(result, showAlerts)

    return result
}

let intervalId // Identifier for the recurring interval

function startTimer(interval) {
    if (!intervalId) {
        // Start only if the interval has not already been set
        intervalId = setInterval(() => {
            handleButtonClick((showAlerts = false))
        }, interval)

        // console.log(`handleButtonClick interval started with ${interval / 1000} seconds.`);
    }
}

// Function to stop the interval
function stopTimer() {
    if (intervalId) {
        clearInterval(intervalId)
        intervalId = null
        // console.log('handleButtonClick interval stopped.');
    }
}

// Observer for adding the send_message button to trigger pushes
const timerButtonObserver = new MutationObserver(() => {
    const startTimerButton = document.querySelector('.send_message')
    if (startTimerButton && !startTimerButton.hasAttribute('data-listener')) {
        startTimerButton.addEventListener('click', () => {
            // console.log('send_message button clicked! Starting initial timer.');
            startTimer(30000)
        })
        startTimerButton.setAttribute('data-listener', 'true')
        // console.log('Handler added to the send_message button.');
    }
})

timerButtonObserver.observe(document.body, { childList: true, subtree: true })

// Observer for adding the send_evaluate button
const buttonObserver = new MutationObserver(() => {
    const button = document.querySelector('.send_evaluate')
    if (button && !button.hasAttribute('data-listener')) {
        button.addEventListener('click', () => {
            handleButtonClick() // Main button functionality
            stopTimer()
        })
        button.setAttribute('data-listener', 'true')
        // console.log('Handler added to the send_evaluate button.');
    }
})

// Start observing DOM changes for the button
buttonObserver.observe(document.body, { childList: true, subtree: true })

// Observer for adding the send_evaluate button
const clearButtonObserver = new MutationObserver(() => {
    const clearButton = document.querySelector('button[aria-label="Clear"]')
    if (clearButton && !clearButton.hasAttribute('data-listener')) {
        clearButton.addEventListener('click', () => {
            stopTimer()
        })
        clearButton.setAttribute('data-listener', 'true')
        // console.log('Handler added to the clear button.');
    }
})

// Start observing DOM changes for the button
clearButtonObserver.observe(document.body, { childList: true, subtree: true })

// Create and launch a MutationObserver to initialize sliders
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    initializeObservers(node) // Initialize for the new node
                }
            })
        }
    })
})

// Observe DOM changes
observer.observe(document.body, { childList: true, subtree: true })

// Initial initialization for existing elements
initializeObservers(document)
