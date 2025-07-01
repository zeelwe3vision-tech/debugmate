import React, { useState } from "react";
import "./project_info.css";

const roleOptions = [
    { label: "Web Development", value: "web" },
    { label: "AI Development", value: "ai" },
    { label: "Graphic Designer", value: "graphic" },
    { label: "UI/UX Designer", value: "uiux" },
    { label: "Metaverse", value: "metaverse" },
];

const roleForms = {
    web: [
        { label: "Favorite Frontend Framework", name: "frontend", type: "text", placeholder: "e.g. React, Vue" },
        { label: "Years of Experience", name: "experience", type: "number", placeholder: "e.g. 3" },
        { label: "Portfolio URL", name: "portfolio", type: "url", placeholder: "https://" },
    ],
    ai: [
        { label: "Preferred AI Language", name: "language", type: "text", placeholder: "e.g. Python" },
        { label: "Familiar Framework", name: "framework", type: "text", placeholder: "e.g. TensorFlow" },
        { label: "AI Project URL", name: "project", type: "url", placeholder: "https://" },
    ],
    graphic: [
        { label: "Favorite Design Tool", name: "tool", type: "text", placeholder: "e.g. Photoshop" },
        { label: "Years of Experience", name: "experience", type: "number", placeholder: "e.g. 2" },
        { label: "Portfolio URL", name: "portfolio", type: "url", placeholder: "https://" },
    ],
    uiux: [
        { label: "Preferred Prototyping Tool", name: "tool", type: "text", placeholder: "e.g. Figma" },
        { label: "Years of Experience", name: "experience", type: "number", placeholder: "e.g. 4" },
        { label: "Portfolio URL", name: "portfolio", type: "url", placeholder: "https://" },
    ],
    metaverse: [
        { label: "Metaverse Platform", name: "platform", type: "text", placeholder: "e.g. Unity, Unreal" },
        { label: "VR/AR Experience", name: "experience", type: "text", placeholder: "e.g. VR, AR, Both" },
        { label: "Portfolio URL", name: "portfolio", type: "url", placeholder: "https://" },
    ],
};

const commonFields = [
    { label: "Project Title", name: "projectTitle", type: "text", placeholder: "Enter project title" },
    { label: "Project Description", name: "projectDescription", type: "textarea", placeholder: "Describe your project" },
    { label: "Team Members", name: "teamMembers", type: "text", placeholder: "e.g. Alice, Bob, Charlie" },
    { label: "Technology Stack", name: "techStack", type: "text", placeholder: "e.g. React, Node.js, MongoDB" },
];

const ProjectInfo = () => {
    const [role, setRole] = useState("");
    const [formData, setFormData] = useState({});

    const handleRoleChange = (e) => {
        setRole(e.target.value);
        // Do not clear common fields
        setFormData((prev) => {
            const { frontend, experience, portfolio, language, framework, project, tool, platform } = prev;
            return {
                ...prev,
                frontend: undefined,
                experience: undefined,
                portfolio: undefined,
                language: undefined,
                framework: undefined,
                project: undefined,
                tool: undefined,
                platform: undefined,
            };
        });
    };

    const handleInputChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        // You can handle form submission here (e.g., send to API)
        alert("Form submitted! " + JSON.stringify(formData, null, 2));
    };

    return (
        <div className="container d-flex align-items-center justify-content-center min-vh-100">
            <div className="card shadow-lg p-4 w-100" style={{ maxWidth: 420 }}>
                <h2 className="h4 font-weight-bold mb-4 text-center">Please give the answer</h2>
                <form onSubmit={handleSubmit} className="fade-in">
                    {/* Common Fields */}
                    {commonFields.map((input) => (
                        <div className="mb-3" key={input.name}>
                            <label className="form-label">{input.label}</label>
                            {input.type === "textarea" ? (
                                <textarea
                                    name={input.name}
                                    value={formData[input.name] || ""}
                                    onChange={handleInputChange}
                                    placeholder={input.placeholder}
                                    className="form-control"
                                    required
                                    rows={3}
                                />
                            ) : (
                                <input
                                    type={input.type}
                                    name={input.name}
                                    value={formData[input.name] || ""}
                                    onChange={handleInputChange}
                                    placeholder={input.placeholder}
                                    className="form-control"
                                    required
                                />
                            )}
                        </div>
                    ))}
                    {/* Role Selection */}
                    <div className="mb-4">
                        <label className="form-label font-weight-medium">Select your role</label>
                        <select
                            className="form-select"
                            value={role}
                            onChange={handleRoleChange}
                            required
                        >
                            <option value="">-- Choose a role --</option>
                            {roleOptions.map((opt) => (
                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                            ))}
                        </select>
                    </div>
                    {/* Role-specific Fields */}
                    {role && (
                        <>
                            {roleForms[role].map((input) => (
                                <div className="mb-3" key={input.name}>
                                    <label className="form-label">{input.label}</label>
                                    <input
                                        type={input.type}
                                        name={input.name}
                                        value={formData[input.name] || ""}
                                        onChange={handleInputChange}
                                        placeholder={input.placeholder}
                                        className="form-control"
                                        required
                                    />
                                </div>
                            ))}
                        </>
                    )}
                    <button
                        type="submit"
                        className="btn btn-primary w-100 mt-2"
                    >
                        Submit
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ProjectInfo;