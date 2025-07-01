import React, { useState } from "react";
import "./project_info.css";
import { Container, Form, Button, Row, Col } from "react-bootstrap";
// import { useNavigate } from "react-router-dom";

const roleOptions = [
    { label: "Web Development", value: "web" },
    { label: "UI/UX Designer", value: "uiux" },
    { label: "Graphic Designer", value: "graphic" },
    { label: "AI Development", value: "ai" },
    { label: "Metaverse", value: "metaverse" },
];

const roleQuestions = {
    web: [
        "Is the project using React?",
        "Does it include a backend service?",
    ],
    uiux: [
        "Is a user persona defined?",
        "Are wireframes completed?",
    ],
    graphic: [
        "Are design assets required?",
        "Is branding provided?",
    ],
    ai: [
        "Is the dataset available?",
        "Does the project involve training a model?",
    ],
    metaverse: [
        "Is it VR enabled?",
        "Does it involve blockchain?",
    ],
};

const yesNoOptions = [
    { label: "Yes", value: "yes" },
    { label: "No", value: "no" },
];

const EmployeeProjectForm = () => {
    const [form, setForm] = useState({
        projectTitle: "",
        projectDescription: "",
        techStack: "",
        teamMembers: "",
        role: [],
        roleAnswers: {},
        customQuestion: "",
        customAnswer: "",
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((prev) => ({ ...prev, [name]: value }));
    };

    const handleRoleAnswer = (q, value) => {
        setForm((prev) => ({
            ...prev,
            roleAnswers: { ...prev.roleAnswers, [q]: value },
        }));
    };

    const handleCustomAnswer = (value) => {
        setForm((prev) => ({ ...prev, customAnswer: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        // Handle form submission (e.g., send to API)
        alert("Form submitted! " + JSON.stringify(form, null, 2));
    };

    const selectedRoles = form.role;
    const questions = selectedRoles.map((role) => roleQuestions[role]).flat();

    return (
        <Container className="project-form-container d-flex align-items-center justify-content-center min-vh-100">
            <Form className="project-form-card p-4" onSubmit={handleSubmit}>
                <h3 className="mb-4 text-center">Employee Project Form</h3>
                {/* Project Details */}
                <Form.Group className="mb-3">
                    <Form.Label>Project Title</Form.Label>
                    <Form.Control
                        type="text"
                        name="projectTitle"
                        value={form.projectTitle}
                        onChange={handleChange}
                        required
                        placeholder="Enter project title"
                    />
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Project Description</Form.Label>
                    <Form.Control
                        as="textarea"
                        name="projectDescription"
                        value={form.projectDescription}
                        onChange={handleChange}
                        rows={3}
                        required
                        placeholder="Describe your project"
                    />
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Tech Stack</Form.Label>
                    <Form.Control
                        type="text"
                        name="techStack"
                        value={form.techStack}
                        onChange={handleChange}
                        required
                        placeholder="e.g. React, Node.js, MongoDB"
                    />
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Team Members</Form.Label>
                    <Form.Control
                        type="text"
                        name="teamMembers"
                        value={form.teamMembers}
                        onChange={handleChange}
                        required
                        placeholder="e.g. Alice, Bob, Charlie"
                    />
                </Form.Group>
                {/* Role Selection */}
                <Form.Group className="mb-4">
                    <Form.Label>Select Role(s)</Form.Label>
                    <div>
                        {roleOptions.map((opt) => (
                            <Form.Check
                                key={opt.value}
                                type="checkbox"
                                id={`role-${opt.value}`}
                                label={opt.label}
                                name="role"
                                value={opt.value}
                                checked={Array.isArray(form.role) ? form.role.includes(opt.value) : false}
                                onChange={() => {
                                    setForm((prev) => {
                                        const currentRoles = Array.isArray(prev.role) ? prev.role : [];
                                        if (currentRoles.includes(opt.value)) {
                                            // Remove role
                                            return { ...prev, role: currentRoles.filter((r) => r !== opt.value) };
                                        } else {
                                            // Add role
                                            return { ...prev, role: [...currentRoles, opt.value] };
                                        }
                                    });
                                }}
                                className="mb-2"
                            />
                        ))}
                    </div>
                </Form.Group>
                {/* Role-based Questions */}
                {questions.length > 0 && (
                    <div className="mb-4">
                        <div className="mb-2 fw-bold">Role-based Questions</div>
                        {questions.map((q, idx) => (
                            <Form.Group as={Row} className="mb-2" key={q}>
                                <Form.Label column sm={8}>{q}</Form.Label>
                                <Col sm={4}>
                                    <Form.Select
                                        value={form.roleAnswers[q] || ""}
                                        onChange={(e) => handleRoleAnswer(q, e.target.value)}
                                        required
                                    >
                                        <option value="">Select</option>
                                        {yesNoOptions.map((opt) => (
                                            <option key={opt.value} value={opt.value}>{opt.label}</option>
                                        ))}
                                    </Form.Select>
                                </Col>
                            </Form.Group>
                        ))}
                    </div>
                )}
                {/* Custom Question */}
                <Form.Group className="mb-3">
                    <Form.Label>Custom Yes/No Question</Form.Label>
                    <Form.Control
                        type="text"
                        name="customQuestion"
                        value={form.customQuestion}
                        onChange={handleChange}
                        placeholder="Type your custom question"
                    />
                </Form.Group>
                {form.customQuestion && (
                    <Form.Group as={Row} className="mb-3">
                        <Form.Label column sm={8}>{form.customQuestion}</Form.Label>
                        <Col sm={4}>
                            <Form.Select
                                value={form.customAnswer}
                                onChange={(e) => handleCustomAnswer(e.target.value)}
                                required
                            >
                                <option value="">Select</option>
                                {yesNoOptions.map((opt) => (
                                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                                ))}
                            </Form.Select>
                        </Col>
                    </Form.Group>
                )}
                <Button type="submit" className="w-100 mt-3" variant="primary">
                    Submit
                </Button>
            </Form>
        </Container>
    );
};

export default EmployeeProjectForm;