# MITRE ATT&CK Mapping

## Attack Chain Overview

This research maps the supply chain attack enabled by LLM hallucinations to the MITRE ATT&CK framework.

## Techniques

### T1195.002: Supply Chain Compromise: Compromise Software Supply Chain

**Description:**
Adversaries compromise software supply chains by introducing malicious code into legitimate software development processes or distribution channels.

**Mapping:**
- **Initial Access:** Attacker registers hallucinated package name on PyPI or npm
- **Persistence:** Malicious payload embedded in package setup.py or installation hooks
- **Execution:** Payload executes when developer runs `pip install` or `npm install`
- **Impact:** Code execution on developer machine during dependency installation

**Relevance:**
This attack vector exploits the fact that developers blindly trust AI-generated code recommendations without verification. The hallucinated package name appears legitimate to the developer, and they have no reason to suspect it.

---

### T1204.002: User Execution: Malicious File

**Description:**
An adversary tricks a user into executing malicious code by social engineering or deception.

**Mapping:**
- **Social Engineering:** AI model recommends non-existent package as if it were real
- **User Action:** Developer copies package name from AI output and installs it
- **Trust Abuse:** Developers trust AI outputs more than they should
- **Execution:** Installation command triggers malicious payload

**Relevance:**
The LLM serves as an unwitting social engineering vector. The AI's authority and apparent knowledge tricks developers into executing code without verification.

---

### T1059: Command and Scripting Interpreter

**Description:**
Adversaries abuse command and script interpreters to execute commands, scripts, or binaries.

**Mapping:**
- **Attack Surface:** Python setup.py scripts and npm postinstall hooks
- **Execution Context:** Package installation runs with developer's user privileges
- **Command Examples:**
  - Python: `python setup.py install` (runs arbitrary code)
  - Node: `npm postinstall` hook (runs arbitrary shell commands)
- **Payload Options:** Reverse shell, credential theft, data exfiltration, persistence

**Relevance:**
Package managers execute arbitrary code during installation. A malicious package can run any command in the installation environment, leading to complete compromise.

---

## Attack Flow

1. Attacker identifies hallucinated package from dataset
2. Attacker registers package on PyPI or npm
3. Developer asks AI to write code for X feature
4. AI recommends hallucinated package (T1204.002: User Execution)
5. Developer copies package name and runs pip install
6. Package installer downloads malicious code
7. setup.py or postinstall hook executes (T1059: Command and Scripting Interpreter)
8. Malicious payload runs with developer privileges (T1195.002 impact)
9. Attacker achieves code execution on developer machine, access to source code and credentials, potential spread to production systems, and supply chain compromise of downstream users

---

## Defense Mapping

### Detection (Blue Team)
- Monitor for installation of packages registered in last 7 days
- Alert on packages with 0 downloads before first installation
- Scan package source for suspicious setup.py/postinstall code
- Implement SlopSquat Shield CLI scanner in developer workflows

### Response
- Revoke compromised accounts
- Audit installed packages and their dependencies
- Scan systems for malicious artifacts
- Notify downstream users of potential compromise