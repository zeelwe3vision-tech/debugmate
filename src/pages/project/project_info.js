import React, { useState } from "react";
import "./project_info.css";
import { Container, Form, Button, Row, Col } from "react-bootstrap";
import projectDatabaseSupabase from '../../services/projectDatabaseSupabase';
import SuccessNotification from './SuccessNotification';
// import { useNavigate } from "react-router-dom";

const roleOptions = [
    { label: "Web Development", value: "web" },
    { label: "UI/UX Designer", value: "uiux" },
    { label: "Graphic Designer", value: "graphic" },
    { label: "AI Development", value: "ai" },
    { label: "Metaverse", value: "metaverse" },
    { label: "AR VR", value: "AV" },
    { label: "SEO and Digital Marketing", value: "SEO " },
    { label: "Digital Designer", value: "digital" },
];

const statusOptions = [
    "Not Started", "In Progress", "Completed", "On Hold"
];
const techStackOptions = [
    "React-js", "Node-js", "MongoDB", "Python", "TensorFlow", "Unity", "Unreal", "Figma", "Photoshop"
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
const teamMembersList = [
];

const EmployeeProjectForm = () => {
    const [form, setForm] = useState({
        projectName: "",
        projectDescription: "",
        startDate: "",
        endDate: "",
        status: "",
        assignedRole: "",
        assignedTo: [],
        priority: "",
        clientName: "",
        uploadDocuments: null,
        projectScope: "",
        techStack: [],
        techStackCustom: "",
        leaderOfProject: "",
        projectResponsibility: "",
        role: [],
        roleAnswers: {},
        customQuestion: "",
        customAnswer: "",
    });
    const [customTeamMember, setCustomTeamMember] = useState("");
    const [customTeamList, setCustomTeamList] = useState([]);
    const [customRole, setCustomRole] = useState("");
    const [customRoleList, setCustomRoleList] = useState([]);
    const [customTech, setCustomTech] = useState("");
    const [customTechList, setCustomTechList] = useState([]);
    const [customQuestion, setCustomQuestion] = useState("");
    const [customQuestionsList, setCustomQuestionsList] = useState([]);
    const [customAnswers, setCustomAnswers] = useState({});
    const [showSuccess, setShowSuccess] = useState(false);
    const handleAddCustomRole = () => {
        const role = customRole.trim();
        if (role && !roleOptions.concat(customRoleList).some(opt => opt.label === role)) {
            setCustomRoleList(prev => [...prev, { label: role, value: role.toLowerCase().replace(/\s+/g, '-') }]);
            setCustomRole("");
        }
    };
    const handleAddCustomTech = () => {
        const tech = customTech.trim();
        if (tech && !techStackOptions.concat(customTechList).includes(tech)) {
            setCustomTechList(prev => [...prev, tech]);
            setCustomTech("");
        }
    };
    const allRoleOptions = [...roleOptions, ...customRoleList];
    const allTechOptions = [...techStackOptions, ...customTechList];
    // For file upload
    const handleFileChange = (e) => {
        const files = Array.from(e.target.files);
        const fileReaders = files.map(file => {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = (event) => {
                    resolve({ name: file.name, data: event.target.result });
                };
                reader.onerror = (err) => reject(err);
                reader.readAsDataURL(file);
            });
        });
        Promise.all(fileReaders).then(fileObjs => {
            setForm((prev) => ({ ...prev, uploadDocuments: fileObjs }));
        });
    };

    const handleChange = (e) => {
        const { name, value, type, } = e.target;
        if (type === "checkbox" && name === "assignedTo") {
            setForm((prev) => {
                const arr = prev.assignedTo.includes(value)
                    ? prev.assignedTo.filter((v) => v !== value)
                    : [...prev.assignedTo, value];
                return { ...prev, assignedTo: arr };
            });
        } else if (type === "checkbox" && name === "techStack") {
            setForm((prev) => {
                const arr = prev.techStack.includes(value)
                    ? prev.techStack.filter((v) => v !== value)
                    : [...prev.techStack, value];
                return { ...prev, techStack: arr };
            });
        } else {
            setForm((prev) => ({ ...prev, [name]: value }));
        }
    };

    const handleRoleChange = (value) => {
        setForm((prev) => {
            const currentRoles = Array.isArray(prev.role) ? prev.role : [];
            if (currentRoles.includes(value)) {
                // Remove role
                return { ...prev, role: currentRoles.filter((r) => r !== value) };
            } else {
                // Add role
                return { ...prev, role: [...currentRoles, value] };
            }
        });
    };

    const handleRoleAnswer = (q, value) => {
        setForm((prev) => ({
            ...prev,
            roleAnswers: { ...prev.roleAnswers, [q]: value },
        }));
    };

    // const handleCustomAnswer = (value) => {
    //     setForm((prev) => ({ ...prev, customAnswer: value }));
    // };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // Save form data to Supabase database
            const result = await projectDatabaseSupabase.saveProject({
                ...form,
                customQuestions: customQuestionsList,
                customAnswers: customAnswers
            });
            if (result.success) {
                setShowSuccess(true);
                // Optionally, reset the form here
            } else {
                alert('Failed to save project: ' + result.message);
            }
        } catch (error) {
            console.error('Error saving project:', error);
            alert('Failed to save project. Please try again.');
        }
    };

    // For team members, show from teamMembersList + customTeamList
    const teamOptions = [...teamMembersList, ...customTeamList.filter(name => !teamMembersList.includes(name))];

    // Handler to add custom team member
    const handleAddCustomTeamMember = () => {
        const name = customTeamMember.trim();
        if (name && !teamOptions.includes(name)) {
            setCustomTeamList((prev) => [...prev, name]);
            setCustomTeamMember("");
        }
    };

    // For leader dropdown, only show from assignedTo
    const leaderOptions = form.assignedTo;

    // Combine and deduplicate questions for all selected roles
    const selectedRoles = form.role;
    const questions = Array.from(new Set(selectedRoles.map((role) => roleQuestions[role]).flat()));

    const handleAddCustomQuestion = () => {
        const question = customQuestion.trim();
        if (question && !customQuestionsList.includes(question)) {
            setCustomQuestionsList(prev => [...prev, question]);
            setCustomQuestion("");
        }
    };

    const handleCustomAnswerChange = (question, value) => {
        setCustomAnswers(prev => ({ ...prev, [question]: value }));
    };

    return (
        <Container className="project-form-container d-flex align-items-center justify-content-center min-vh-99" style={{ flexDirection: 'column' }}>
            <SuccessNotification show={showSuccess} message="Your form data has been successfully saved!" onClose={() => setShowSuccess(false)} />
            <Form className="project-form-card p-4" onSubmit={handleSubmit}>
                <h3 className="mb-4 text-center">Employee Project Form</h3>
                {/* Default Questions */}
                <Form.Group className="mb-3">
                    <Form.Label>Project Name</Form.Label>
                    <Form.Control
                        type="text"
                        name="projectName"
                        value={form.projectName}
                        onChange={handleChange}
                        required
                        placeholder="Name/title of the project"
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
                        placeholder="Summary or purpose of the project"
                    />
                </Form.Group>
                <Row>
                    <Col md={6}>
                        <Form.Group className="mb-3">
                            <Form.Label>Start Date</Form.Label>
                            <Form.Control
                                type="date"
                                name="startDate"
                                value={form.startDate}
                                onChange={handleChange}
                                required
                            />
                        </Form.Group>
                    </Col>
                    <Col md={6}>
                        <Form.Group className="mb-3">
                            <Form.Label>End Date</Form.Label>
                            <Form.Control
                                type="date"
                                name="endDate"
                                value={form.endDate}
                                onChange={handleChange}
                                required
                            />
                        </Form.Group>
                    </Col>
                </Row>
                <Form.Group className="mb-3">
                    <Form.Label>Status</Form.Label>
                    <Form.Select
                        name="status"
                        value={form.status}
                        onChange={handleChange}
                        required
                    >
                        <option value="">Select status</option>
                        {statusOptions.map((opt) => (
                            <option key={opt} value={opt}>{opt}</option>
                        ))}
                    </Form.Select>
                </Form.Group>
                <Form.Group className="mb-3">
    <Form.Label>Team Member Emails</Form.Label>
    <div className="d-flex">
        <Form.Control
            type="email"
            placeholder="Enter team member email"
            value={customTeamMember}
            onChange={(e) => setCustomTeamMember(e.target.value)}
            className="me-2"
        />
        <Button
            variant="outline-primary"
            type="button"
            onClick={() => {
                const email = customTeamMember.trim();
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(email)) {
                    alert("Please enter a valid email address.");
                    return;
                }
                if (!form.assignedTo.includes(email)) {
                    setForm((prev) => ({
                        ...prev,
                        assignedTo: [...prev.assignedTo, email]
                    }));
                }
                setCustomTeamMember("");
            }}
            disabled={!customTeamMember.trim()}
        >
            Add
        </Button>
    </div>

    {form.assignedTo.length > 0 && (
        <ul className="email-list mt-2">
            {form.assignedTo.map((email, idx) => (
                <li key={idx} className="email-item fade-in">
                    <span>{email}</span>
                    <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => {
                            setForm((prev) => ({
                                ...prev,
                                assignedTo: prev.assignedTo.filter((e) => e !== email)
                            }));
                        }}
                    >
                        ✕
                    </Button>
                </li>
            ))}
        </ul>
    )}
</Form.Group>


                <Form.Group className="mb-3">
                    <Form.Label>Client Name/Owner Name</Form.Label>
                    <Form.Control
                        type="text"
                        name="clientName"
                        value={form.clientName}
                        onChange={handleChange}
                        placeholder="Add client name if applicable"
                    />
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Upload Documents</Form.Label>
                    <Form.Control
                        type="file"
                        name="uploadDocuments"
                        onChange={handleFileChange}
                        multiple
                    />
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Project Scope</Form.Label>
                    <Form.Control
                        as="textarea"
                        name="projectScope"
                        value={form.projectScope}
                        onChange={handleChange}
                        rows={2}
                        placeholder="Scope of projects"
                    />
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Technology Stack</Form.Label>
                    <div>
                        {allTechOptions.map((tech) => (
                            <Form.Check
                                key={tech}
                                type="checkbox"
                                id={`techStack-${tech}`}
                                label={tech}
                                name="techStack"
                                value={tech}
                                checked={form.techStack.includes(tech)}
                                onChange={handleChange}
                                className="mb-2"
                            />
                        ))}
                        <div className="d-flex mt-2">
                            <Form.Control
                                type="text"
                                value={customTech}
                                onChange={e => setCustomTech(e.target.value)}
                                placeholder="Add custom technology"
                                className="me-2"
                            />
                            <Button variant="outline-primary" type="button" onClick={handleAddCustomTech} disabled={!customTech.trim()}>
                                Add
                            </Button>
                        </div>
                    </div>
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Leader of Project</Form.Label>
                    <Form.Select
                        name="leaderOfProject"
                        value={form.leaderOfProject}
                        onChange={handleChange}
                        required={leaderOptions.length > 0}
                        disabled={leaderOptions.length === 0}
                    >
                        <option value="">Select leader</option>
                        {leaderOptions.map((member) => (
                            <option key={member} value={member}>{member}</option>
                        ))}
                    </Form.Select>
                </Form.Group>
                <Form.Group className="mb-3">
                    <Form.Label>Project Responsibility</Form.Label>
                    <Form.Control
                        type="text"
                        name="projectResponsibility"
                        value={form.projectResponsibility}
                        onChange={handleChange}
                        placeholder="Description of assigned team members"
                    />
                </Form.Group>
                {/* Role Selection (multi) */}
                <Form.Group className="mb-4">
                    <Form.Label>Select Role(s)</Form.Label>
                    <div>
                        {allRoleOptions.map((opt) => (
                            <Form.Check
                                key={opt.value}
                                type="checkbox"
                                id={`role-${opt.value}`}
                                label={opt.label}
                                name="role"
                                value={opt.value}
                                checked={Array.isArray(form.role) ? form.role.includes(opt.value) : false}
                                onChange={() => handleRoleChange(opt.value)}
                                className="mb-2"
                            />
                        ))}
                        <div className="d-flex mt-2">
                            <Form.Control
                                type="text"
                                placeholder="Add custom Role"
                                value={customRole}
                                onChange={e => setCustomRole(e.target.value)}
                                className="me-2"
                            />
                            <Button variant="outline-primary" type="button" onClick={handleAddCustomRole} disabled={!customRole.trim()}>
                                Add
                            </Button>
                        </div>
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
                    <Form.Label>Custom Question</Form.Label>
                    <div className="d-flex">
                        <Form.Control
                            type="text"
                            value={customQuestion}
                            onChange={e => setCustomQuestion(e.target.value)}
                            placeholder="Type your custom question"
                            className="me-2"
                        />
                        <Button variant="outline-primary" type="button" onClick={handleAddCustomQuestion} disabled={!customQuestion.trim()}>
                            Add
                        </Button>
                    </div>
                </Form.Group>
                {customQuestionsList.map((q, idx) => (
                    <Form.Group as={Row} className="mb-3" key={q}>
                        <Form.Label column sm={8}>{q}</Form.Label>
                        <Col sm={4}>
                            <Form.Control
                                as="textarea"
                                rows={2}
                                value={customAnswers[q] || ""}
                                onChange={e => handleCustomAnswerChange(q, e.target.value)}
                                required
                                placeholder="Type your answer"
                            />
                        </Col>
                    </Form.Group>
                ))}
                <Button type="submit" className="w-100 mt-3" variant="primary">
                    Submit
                </Button>
            </Form>
        </Container>
    );
};

export default EmployeeProjectForm;
