document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("skillForm");
    if (!form) return;

    const resumeFile = document.getElementById("resumeFile");
    const jobDescription = document.getElementById("jobDescription");
    const results = document.getElementById("results");

    // Dashboard data
    function getSaved(key, fallback) {
        try {
            const value = localStorage.getItem(key);
            return value ? JSON.parse(value) : fallback;
        } catch {
            return fallback;
        }
    }

    function saveData(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error("Could not save dashboard data:", error);
        }
    }

    let totalAnalyses = getSaved("skillmapAnalyses", 0);
    let completedSkills = getSaved("skillmapCompleted", []);
    let currentRequiredSkills = getSaved("skillmapRequired", []);

    function updateDashboard(matched = 0, missing = 0, percentage = 0) {
        document.getElementById("totalAnalyses").textContent = totalAnalyses;
        document.getElementById("latestMatch").textContent = percentage + "%";
        document.getElementById("totalMatched").textContent = matched;
        document.getElementById("totalMissing").textContent = missing;

        const completedCount = currentRequiredSkills.filter(
            skill => completedSkills.includes(skill)
        ).length;

        const progress = currentRequiredSkills.length
            ? Math.round(
                (completedCount / currentRequiredSkills.length) * 100
            )
            : 0;

        document.getElementById("completedSkills").textContent =
            completedCount + " skills completed";

        document.getElementById("learningProgress").style.width =
            progress + "%";

        document.getElementById("progressPercentage").textContent =
            progress + "% completed";
    }

    updateDashboard(
        getSaved("skillmapMatched", 0),
        getSaved("skillmapMissing", 0),
        getSaved("skillmapLatestMatch", 0)
    );

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, char => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        })[char]);
    }

    function safeURL(value) {
        try {
            const url = new URL(value);
            return ["https:", "http:"].includes(url.protocol)
                ? url.href
                : "#";
        } catch {
            return "#";
        }
    }

    function renderSkills(skills, type) {
        if (!Array.isArray(skills) || skills.length === 0) {
            return `<p class="empty-message">No skills found.</p>`;
        }

        return `
            <div class="skill-tags ${type}">
                ${skills.map(skill =>
                    `<span class="skill-tag">${escapeHTML(skill)}</span>`
                ).join("")}
            </div>
        `;
    }

    function renderRecommendations(items) {
        if (!Array.isArray(items) || items.length === 0) {
            return `<p>No course recommendations available.</p>`;
        }

        return `
            <div class="recommendation-grid">
                ${items.map(item => {
                    const skill = String(item.skill || "Skill");
                    const learned = completedSkills.includes(skill);

                    return `
                        <div class="recommendation-card">
                            <h3>${escapeHTML(skill)}</h3>
                            <p>${escapeHTML(item.course || "Learning Resource")}</p>

                            <a href="${safeURL(item.link)}"
                               target="_blank"
                               rel="noopener noreferrer"
                               class="course-button">
                               Start Learning
                            </a>

                            <button type="button"
                                class="learned-button"
                                data-skill="${escapeHTML(skill)}"
                                ${learned ? "disabled" : ""}>
                                ${learned ? "Learned ✓" : "Mark as Learned"}
                            </button>
                        </div>
                    `;
                }).join("")}
            </div>
        `;
    }

    // Mark a recommended skill as learned
    results.addEventListener("click", event => {
        const button = event.target.closest(".learned-button");
        if (!button || button.disabled) return;

        const skill = button.dataset.skill;

        if (!completedSkills.includes(skill)) {
            completedSkills.push(skill);
            saveData("skillmapCompleted", completedSkills);
        }

        button.textContent = "Learned ✓";
        button.disabled = true;

        updateDashboard(
            getSaved("skillmapMatched", 0),
            getSaved("skillmapMissing", 0),
            getSaved("skillmapLatestMatch", 0)
        );
    });

    form.addEventListener("submit", async function(event) {
        event.preventDefault();

        if (!resumeFile.files.length) {
            alert("Please upload your resume.");
            return;
        }

        if (!jobDescription.value.trim()) {
            alert("Please enter the job description.");
            return;
        }

        const file = resumeFile.files[0];
        const allowedExtensions = [".pdf", ".docx", ".txt"];
        const extension = file.name.toLowerCase().slice(
            file.name.lastIndexOf(".")
        );

        if (!allowedExtensions.includes(extension)) {
            alert("Please upload a PDF, DOCX or TXT resume.");
            return;
        }

        const formData = new FormData();
        formData.append("resume", file);
        formData.append("jobDescription", jobDescription.value.trim());

        const button = form.querySelector('button[type="submit"]');
        const originalText = button.textContent;

        button.textContent = "Analyzing...";
        button.disabled = true;

        results.innerHTML = `
            <div class="loading-message">
                <h2>Analyzing Your Resume...</h2>
                <p>Please wait while SkillMap compares your skills.</p>
            </div>
        `;

        try {
            const response = await fetch("/analyze", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Analysis failed.");
            }

            const matchedSkills = data.matched_skills || [];
            const missingSkills = data.missing_skills || [];
            const resumeSkills = data.resume_skills || [];
            const requiredSkills = data.required_skills || [];
            const recommendations = data.recommendations || [];

            const percentage = Math.min(
                100,
                Math.max(0, Number(data.match_percentage) || 0)
            );

            // Update and save dashboard statistics
            totalAnalyses++;
            currentRequiredSkills = requiredSkills;

            saveData("skillmapAnalyses", totalAnalyses);
            saveData("skillmapRequired", currentRequiredSkills);
            saveData("skillmapMatched", matchedSkills.length);
            saveData("skillmapMissing", missingSkills.length);
            saveData("skillmapLatestMatch", percentage);

            updateDashboard(
                matchedSkills.length,
                missingSkills.length,
                percentage
            );

            results.innerHTML = `
                <div class="results-container">
                    <h2>Skill Analysis Results</h2>

                    <div class="match-card">
                        <h3>Resume Match Percentage</h3>
                        <div class="match-number">${percentage}%</div>

                        <div class="progress-track">
                            <div class="progress-fill"
                                 style="width: ${percentage}%"></div>
                        </div>

                        <p>
                            ${percentage >= 75
                                ? "Great! Your resume matches this job well."
                                : percentage >= 50
                                ? "Good progress! Improve your missing skills."
                                : "Keep learning to improve your job readiness."}
                        </p>
                    </div>

                    <div class="result-card matched-card">
                        <h3>Matched Skills</h3>
                        ${renderSkills(matchedSkills, "matched")}
                    </div>

                    <div class="result-card missing-card">
                        <h3>Missing Skills</h3>
                        ${renderSkills(missingSkills, "missing")}
                    </div>

                    <div class="result-card resume-card">
                        <h3>Resume Skills</h3>
                        ${renderSkills(resumeSkills, "resume")}
                    </div>

                    <div class="result-card courses-card">
                        <h2>Learning Recommendations</h2>
                        <p>Explore these resources to improve your skills.</p>
                        ${renderRecommendations(recommendations)}
                    </div>

                    <div class="download-section">
                        <h3>Your report is ready!</h3>
                        <button type="button" id="downloadReport">
                            Download PDF Report
                        </button>
                    </div>
                </div>
            `;

            document.getElementById("downloadReport")
                .addEventListener("click", async () => {
                    const downloadButton =
                        document.getElementById("downloadReport");

                    downloadButton.disabled = true;
                    downloadButton.textContent = "Preparing PDF...";

                    try {
                        const pdfResponse = await fetch("/download-report", {
                            method: "POST",
                            body: formData
                        });

                        if (!pdfResponse.ok) {
                            const errorData = await pdfResponse.json();
                            throw new Error(
                                errorData.error || "PDF download failed."
                            );
                        }

                        const blob = await pdfResponse.blob();
                        const url = URL.createObjectURL(blob);
                        const link = document.createElement("a");

                        link.href = url;
                        link.download = "SkillMap_Report.pdf";
                        document.body.appendChild(link);
                        link.click();
                        link.remove();

                        URL.revokeObjectURL(url);
                        downloadButton.textContent = "Download Again";

                    } catch (error) {
                        alert(error.message);
                        downloadButton.textContent = "Download PDF Report";
                    } finally {
                        downloadButton.disabled = false;
                    }
                });

            results.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        } catch (error) {
            results.innerHTML = `
                <div class="error-message">
                    <h3>Something went wrong</h3>
                    <p>${escapeHTML(error.message)}</p>
                    <p>Please check and try again.</p>
                </div>
            `;
        } finally {
            button.textContent = originalText;
            button.disabled = false;
        }
    });
});