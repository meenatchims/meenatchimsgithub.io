// Career Assessment
document.getElementById('careerAssessmentForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Collect form data
    const formData = {
        education: document.getElementById('education').value,
        experience: document.getElementById('experience').value,
        skills: Array.from(document.querySelectorAll('.skill-tag')).map(tag => 
            tag.textContent.replace('×', '').trim()),
        interests: document.getElementById('interests').value,
        workLifeBalance: document.getElementById('workLifeBalance').value,
        salaryImportance: document.getElementById('salaryImportance').value,
        location: document.getElementById('location').value
    };
    
    // Show loading state
    const submitBtn = this.querySelector('.btn-submit');
    submitBtn.textContent = 'Analyzing...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/assess-career', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Display results
            const resultsContainer = document.getElementById('results-section');
            resultsContainer.innerHTML = `
                <h3>Your AI-Recommended Career Paths</h3>
                ${data.recommendations.map(career => `
                    <div class="career-match">
                        <div class="match-score">${career.matchScore}%</div>
                        <div class="career-info">
                            <h4>${career.title}</h4>
                            <p>${career.description}</p>
                            <div class="career-tags">
                                ${career.tags.map(tag => `<span class="career-tag">${tag}</span>`).join('')}
                                <span class="career-tag">${career.salaryRange}</span>
                            </div>
                            <p><strong>Next Steps:</strong> ${career.nextSteps}</p>
                        </div>
                    </div>
                `).join('')}
            `;
            
            resultsContainer.style.display = 'block';
            resultsContainer.classList.add('fade-in');
            resultsContainer.scrollIntoView({ behavior: 'smooth' });
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Failed to get recommendations. Please try again.');
        console.error(error);
    } finally {
        submitBtn.textContent = 'Get Career Recommendations';
        submitBtn.disabled = false;
    }
});

// Resume Builder
async function generateResume() {
    const formData = {
        name: document.getElementById('resume-name').value,
        contact: document.getElementById('resume-contact').value,
        summary: document.getElementById('resume-summary').value,
        experience: document.getElementById('resume-experience').value,
        education: document.getElementById('resume-education').value,
        skills: Array.from(document.querySelectorAll('.resume-skill-tag')).map(tag => 
            tag.textContent.replace('×', '').trim())
    };
    
    if (!formData.name || !formData.summary || !formData.experience) {
        alert('Please fill in all required fields');
        return;
    }
    
    const generateBtn = document.getElementById('generate-resume-btn');
    generateBtn.textContent = 'Generating...';
    generateBtn.disabled = true;
    
    try {
        const response = await fetch('/generate-resume', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            document.getElementById('resume-output').innerHTML = data.resume;
            document.getElementById('resume-preview').style.display = 'block';
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Failed to generate resume. Please try again.');
        console.error(error);
    } finally {
        generateBtn.textContent = 'Generate Resume';
        generateBtn.disabled = false;
    }
}

// Interview Preparation
async function generateInterviewQuestions() {
    const formData = {
        jobRole: document.getElementById('interview-job-role').value,
        experienceLevel: document.getElementById('interview-experience').value,
        company: document.getElementById('interview-company').value
    };
    
    if (!formData.jobRole) {
        alert('Please enter a job role');
        return;
    }
    
    const generateBtn = document.getElementById('generate-questions-btn');
    generateBtn.textContent = 'Generating...';
    generateBtn.disabled = true;
    
    try {
        const response = await fetch('/generate-interview-questions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            const questionsContainer = document.getElementById('interview-questions');
            questionsContainer.innerHTML = data.questions.map((q, i) => `
                <div class="question-card">
                    <h4>Question ${i+1}: ${q.question}</h4>
                    <p><strong>Why they ask this:</strong> ${q.purpose}</p>
                    <p><strong>Tips:</strong> ${q.tips}</p>
                    <p><strong>Sample answer:</strong> ${q.sampleAnswer}</p>
                </div>
            `).join('');
            
            document.getElementById('interview-results').style.display = 'block';
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Failed to generate questions. Please try again.');
        console.error(error);
    } finally {
        generateBtn.textContent = 'Generate Questions';
        generateBtn.disabled = false;
    }
}

// Job Search
async function searchJobs() {
    const formData = {
        jobTitle: document.getElementById('search-job-title').value,
        location: document.getElementById('search-location').value,
        experienceLevel: document.getElementById('search-experience').value
    };
    
    if (!formData.jobTitle) {
        alert('Please enter a job title');
        return;
    }
    
    const searchBtn = document.getElementById('search-jobs-btn');
    searchBtn.textContent = 'Searching...';
    searchBtn.disabled = true;
    
    try {
        const response = await fetch('/search-jobs', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            const jobsContainer = document.getElementById('job-listings');
            jobsContainer.innerHTML = data.jobs.map(job => `
                <div class="job-card">
                    <h3>${job.title} at ${job.company}</h3>
                    <p><strong>Location:</strong> ${job.location}</p>
                    <p><strong>Salary:</strong> ${job.salaryRange}</p>
                    <p>${job.description}</p>
                    <button class="apply-btn" data-link="${job.applicationLink}">Apply Now</button>
                </div>
            `).join('');
            
            const tipsContainer = document.getElementById('job-tips');
            tipsContainer.innerHTML = `
                <h3>Application Tips</h3>
                <ul>
                    ${data.tips.map(tip => `<li>${tip}</li>`).join('')}
                </ul>
            `;
            
            document.getElementById('job-results').style.display = 'block';
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Failed to search for jobs. Please try again.');
        console.error(error);
    } finally {
        searchBtn.textContent = 'Search Jobs';
        searchBtn.disabled = false;
    }
}

// Skill Development
async function analyzeSkills() {
    const formData = {
        currentSkills: Array.from(document.querySelectorAll('.current-skill-tag')).map(tag => 
            tag.textContent.replace('×', '').trim()),
        desiredCareer: document.getElementById('desired-career').value
    };
    
    if (!formData.currentSkills.length || !formData.desiredCareer) {
        alert('Please fill in all fields');
        return;
    }
    
    const analyzeBtn = document.getElementById('analyze-skills-btn');
    analyzeBtn.textContent = 'Analyzing...';
    analyzeBtn.disabled = true;
    
    try {
        const response = await fetch('/analyze-skills', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            const analysis = data.analysis;
            
            document.getElementById('skill-gap-analysis').innerHTML = `
                <h3>Skill Gap Analysis</h3>
                <p><strong>Your current skills:</strong> ${analysis.currentSkills.join(', ')}</p>
                <p><strong>Required skills for ${formData.desiredCareer}:</strong> ${analysis.requiredSkills.join(', ')}</p>
                <p><strong>Skills to develop:</strong> ${analysis.skillsToDevelop.join(', ')}</p>
            `;
            
            document.getElementById('learning-resources').innerHTML = `
                <h3>Learning Resources</h3>
                ${analysis.learningResources.map(resource => `
                    <div class="resource-card">
                        <h4>${resource.skill}</h4>
                        <ul>
                            ${resource.resources.map(item => `
                                <li><a href="${item.link}" target="_blank">${item.name}</a></li>
                            `).join('')}
                        </ul>
                    </div>
                `).join('')}
            `;
            
            document.getElementById('learning-plan').innerHTML = `
                <h3>3-Month Learning Plan</h3>
                <p>${analysis.learningPlan}</p>
            `;
            
            document.getElementById('skill-results').style.display = 'block';
        } else {
            alert('Error: ' + data.message);
        }
    } catch (error) {
        alert('Failed to analyze skills. Please try again.');
        console.error(error);
    } finally {
        analyzeBtn.textContent = 'Analyze Skills';
        analyzeBtn.disabled = false;
    }
}

// Helper function for skill tags
function setupSkillInput(inputId, containerId) {
    const input = document.getElementById(inputId);
    const container = document.getElementById(containerId);
    
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && this.value.trim() !== '') {
            e.preventDefault();
            
            const skillTag = document.createElement('div');
            skillTag.className = containerId === 'skills-container' ? 'skill-tag' : 'current-skill-tag';
            skillTag.innerHTML = `
                ${this.value.trim()}
                <span class="remove-skill">×</span>
            `;
            
            skillTag.querySelector('.remove-skill').addEventListener('click', function() {
                skillTag.remove();
            });
            
            container.appendChild(skillTag);
            this.value = '';
        }
    });
}

// Initialize skill inputs
document.addEventListener('DOMContentLoaded', function() {
    setupSkillInput('skills', 'skills-container');
    setupSkillInput('current-skills-input', 'current-skills-container');
});