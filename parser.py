import spacy
import pdfplumber
import re
import os

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    import subprocess
    subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
    nlp = spacy.load('en_core_web_sm')

# Skills database
SKILLS_DB = [
    'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go',
    'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring',
    'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'linux',
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'nlp', 'computer vision',
    'data analysis', 'data science', 'pandas', 'numpy', 'scikit-learn', 'tableau', 'power bi',
    'agile', 'scrum', 'jira', 'project management', 'communication', 'leadership'
]

# Education keywords
EDUCATION_KEYWORDS = [
    'b.tech', 'b.e', 'b.sc', 'm.tech', 'm.e', 'm.sc', 'mba', 'phd', 'bachelor', 'master',
    'diploma', 'bca', 'mca', 'b.com', 'm.com', 'engineering', 'computer science', 'information technology'
]

def extract_text_from_pdf(filepath):
    """Extract text from PDF file"""
    text = ''
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'
    except Exception as e:
        print(f"Error extracting PDF: {e}")
    return text

def extract_name(text, doc):
    """Extract name from resume"""
    # Try to get PERSON entity from first few lines
    lines = text.split('\n')[:5]
    for line in lines:
        line_doc = nlp(line.strip())
        for ent in line_doc.ents:
            if ent.label_ == 'PERSON':
                return ent.text
    
    # Fallback: first capitalized words
    for line in lines:
        words = line.strip().split()
        if len(words) >= 2:
            if words[0][0].isupper() and words[1][0].isupper():
                return ' '.join(words[:2])
    
    return 'Unknown'

def extract_email(text):
    """Extract email from text"""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else ''

def extract_phone(text):
    """Extract phone number from text"""
    phone_patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\d{10}',
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'
    ]
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            return phones[0]
    return ''

def extract_skills(text):
    """Extract skills from text"""
    text_lower = text.lower()
    found_skills = []
    for skill in SKILLS_DB:
        if skill.lower() in text_lower:
            found_skills.append(skill.title())
    return list(set(found_skills))

def extract_education(text):
    """Extract education from text"""
    text_lower = text.lower()
    education = []
    for keyword in EDUCATION_KEYWORDS:
        if keyword in text_lower:
            # Find the line containing this keyword
            for line in text.split('\n'):
                if keyword in line.lower():
                    education.append(line.strip())
                    break
    return education[:3]  # Return top 3 education entries

def extract_experience(text):
    """Extract work experience from text"""
    experience_keywords = ['experience', 'work history', 'employment', 'career']
    lines = text.split('\n')
    experience = []
    capture = False
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        if any(kw in line_lower for kw in experience_keywords):
            capture = True
            continue
        if capture and line.strip():
            if any(kw in line_lower for kw in ['education', 'skills', 'projects', 'certifications']):
                break
            experience.append(line.strip())
            if len(experience) >= 5:
                break
    
    return experience

def parse_resume(filepath):
    """Main function to parse resume and extract information"""
    # Extract text
    if filepath.lower().endswith('.pdf'):
        text = extract_text_from_pdf(filepath)
    else:
        # For other file types, try reading as text
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except:
            text = ''
    
    if not text:
        return {
            'name': 'Unknown',
            'email': '',
            'phone': '',
            'skills': [],
            'education': [],
            'experience': [],
            'raw_text': ''
        }
    
    # Process with spaCy
    doc = nlp(text[:100000])  # Limit text length for processing
    
    # Extract information
    data = {
        'name': extract_name(text, doc),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'skills': extract_skills(text),
        'education': extract_education(text),
        'experience': extract_experience(text),
        'raw_text': text[:1000]  # Store first 1000 chars
    }
    
    return data
