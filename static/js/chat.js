document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const teacherMessages = document.getElementById('teacher-messages');
    const studentMessages = document.getElementById('student-messages');
    
    // Get active tab
    function getActiveUserType() {
        const teacherTab = document.getElementById('teacher-tab');
        return teacherTab.classList.contains('active') ? 'teacher' : 'student';
    }
    
    // Get messages container based on user type
    function getMessagesContainer() {
        const userType = getActiveUserType();
        return userType === 'teacher' ? teacherMessages : studentMessages;
    }
    
    // Add message to chat
    function addMessage(content, isUser = false) {
        const messagesContainer = getMessagesContainer();
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const messagePara = document.createElement('p');
        messagePara.textContent = content;
        
        messageContent.appendChild(messagePara);
        messageDiv.appendChild(messageContent);
        messagesContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Demo responses (for the landing page only)
    function getDemoResponse(message, userType) {
        if (userType === 'teacher') {
            if (message.toLowerCase().includes('lesson') || message.toLowerCase().includes('plan')) {
                return "I can help create a lesson plan! What subject and grade level are you teaching?";
            } else if (message.toLowerCase().includes('assignment') || message.toLowerCase().includes('quiz')) {
                return "I'd be happy to help generate an assignment or quiz. What topic are you covering?";
            } else {
                return "As your teaching assistant, I can help with lesson planning, content creation, assessment ideas, and teaching strategies. What specific area would you like assistance with?";
            }
        } else {
            if (message.toLowerCase().includes('career') || message.toLowerCase().includes('job')) {
                return "I'd be happy to provide career guidance! What subjects or activities do you enjoy the most?";
            } else if (message.toLowerCase().includes('help') || message.toLowerCase().includes('understand')) {
                return "I can definitely help explain that concept. What specific part are you finding difficult?";
            } else {
                return "As your learning assistant, I can help with understanding concepts, provide study tips, or discuss career paths. What would you like to know more about?";
            }
        }
    }
    
    // Handle form submission
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const message = messageInput.value.trim();
            if (message === '') return;
            
            // Get user type (teacher or student)
            const userType = getActiveUserType();
            
            // Add user message to chat
            addMessage(message, true);
            
            // Clear input
            messageInput.value = '';
            
            // On the landing page, we'll just use demo responses
            // In the actual app, this would call the AI service backend
            setTimeout(() => {
                const response = getDemoResponse(message, userType);
                addMessage(response);
            }, 1000);
        });
    }
});
