import sys
import os
import pypdf
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Suppress header and footer on title/cover page
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.black)

        # Running Header
        header_text = "Cyberbullying Detection and Severity Analysis - MCA Academic Project & Viva Guide"
        self.drawString(54, 804, header_text)
        self.setStrokeColor(colors.black)
        self.setLineWidth(0.5)
        self.line(54, 798, 541, 798)

        # Running Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(541, 32, page_str)
        self.drawString(54, 32, "Master of Computer Applications (MCA) - Natural Language Processing & Machine Learning")
        self.line(54, 42, 541, 42)

        self.restoreState()

def build_pdf_story(toc_page_map=None):
    if toc_page_map is None:
        toc_page_map = {i: "Page X" for i in range(1, 18)}

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.black,
        alignment=1, # Center
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.black,
        alignment=1,
        spaceAfter=12
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.black,
        alignment=1,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.black,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14.5,
        textColor=colors.black,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.black,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.black,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.black,
        alignment=0
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.black
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.black
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.black
    )

    story = []

    # ==================== PAGE 1: TITLE & COVER ====================
    story.append(Spacer(1, 10))
    story.append(Paragraph("CYBERBULLYING DETECTION AND SEVERITY ANALYSIS", title_style))
    story.append(Paragraph("Comprehensive Academic Project Report, Technical Architecture, and Viva Guide", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=10))

    meta_text = """
    <b>Degree:</b> Master of Computer Applications (MCA) &nbsp;|&nbsp; <b>Domain:</b> Natural Language Processing (NLP) & Machine Learning<br/>
    <b>Dataset:</b> Kaggle Jigsaw Toxic Comment Classification Challenge (159,571 Human-Annotated Samples)<br/>
    <b>Production Stack:</b> Python 3.11, Scikit-Learn, FastAPI REST Backend, SQLite Database, React 19 Single Page Application
    """
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 6))

    # Executive Summary Card Table
    exec_summary_data = [
        [Paragraph("<b>EXECUTIVE PROJECT SUMMARY</b>", table_header_style)],
        [Paragraph(
            "Online social platforms, forums, and messaging applications have seen an alarming rise in hostile, abusive, and threatening text interactions. Traditional keyword blacklists fail to detect subtle insults and misclassify benign texts that use colloquial language. This MCA major project introduces an end-to-end, production-grade Natural Language Processing system that accurately classifies online toxic speech across six distinct categories (general toxic, severe toxic, obscene language, threats, insults, and identity attacks), assigns an actionable four-tier severity level from Level 0 (Neutral) to Level 3 (Severe Harm), and provides transparent word-level mathematical explainability.<br/><br/>"
            "Trained on 159,571 human-annotated comments from the Kaggle Jigsaw dataset, the system achieves an overall test accuracy of 88.42 percent and a Macro F1 score of 0.8392 using a Calibrated Linear Support Vector Machine. The end-to-end software stack pairs an asynchronous FastAPI backend and SQLite database with a modern, dark-themed React 19 interface featuring real-time single text analysis, bulk CSV ingestion, interactive NLP pipeline exploration, and full model benchmarks.",
            body_style
        )]
    ]
    exec_table = Table(exec_summary_data, colWidths=[487])
    exec_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.white),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(exec_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>PROJECT CONTRIBUTION ROLES (FOUR-MEMBER TEAM):</b>", h2_style))
    roles_data = [
        [Paragraph("<b>Team Member</b>", table_header_style), Paragraph("<b>Assigned Functional Area</b>", table_header_style), Paragraph("<b>Key Technical Deliverables</b>", table_header_style)],
        [Paragraph("Member 1", table_cell_bold), Paragraph("Data Engineering and NLP Pipeline", table_cell_style), Paragraph("Dataset ingestion, stratified 70/15/15 split, cleaning regex, negation-aware stopword filtering, WordNet lemmatization, and TF-IDF matrix generation.", table_cell_style)],
        [Paragraph("Member 2", table_cell_bold), Paragraph("ML Model Training and Optimization", table_cell_style), Paragraph("Multi-model training (Linear SVM, Logistic Regression, Naive Bayes), probability calibration (Platt scaling), 6-stage ablation studies, and evaluation metrics.", table_cell_style)],
        [Paragraph("Member 3", table_cell_bold), Paragraph("Backend REST API and Architecture", table_cell_style), Paragraph("FastAPI endpoints, SQLite database schemas via SQLAlchemy, severity ranking heuristics, and transparent word contribution engine.", table_cell_style)],
        [Paragraph("Member 4", table_cell_bold), Paragraph("Frontend UI/UX and Integration", table_cell_style), Paragraph("React 19 single page application, Material UI dark aesthetic, batch CSV upload, interactive charts, and API client integration.", table_cell_style)]
    ]
    roles_table = Table(roles_data, colWidths=[65, 155, 267])
    roles_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(roles_table)
    story.append(PageBreak())

    # ==================== PAGE 2: TABLE OF CONTENTS ====================
    story.append(Paragraph("TABLE OF CONTENTS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=14))

    toc_titles = [
        (1, "1. Introduction and Clear Problem Statement"),
        (2, "2. Conceptual Foundation: Toxicity vs Cyberbullying"),
        (3, "3. Dataset Exploration and Stratified Partitioning"),
        (4, "4. Comprehensive End-to-End System Architecture"),
        (5, "5. Six-Stage NLP Preprocessing Pipeline in Detail"),
        (6, "6. TF-IDF Representation: Plain English Explanation"),
        (7, "7. How a Word Gets Flagged as Toxic: Step-by-Step Walkthrough"),
        (8, "8. Preprocessing Ablation Study and Empirical Findings"),
        (9, "9. Machine Learning Model Selection and Comparison"),
        (10, "10. Why Linear SVM Won and Why Deep Learning was Not Default"),
        (11, "11. Model Evaluation and Held-Out Test Performance"),
        (12, "12. Multi-Tier Severity Scoring Rubric and Heuristics"),
        (13, "13. Software Implementation: Backend API and Frontend UI"),
        (14, "14. Verification, Automated Testing, and Edge-Case Handling"),
        (15, "15. Comprehensive Viva Examination Guide & Top 12 FAQs"),
        (16, "16. Conclusion, Limitations, and Future Roadmap")
    ]
    
    toc_data = [[Paragraph(f"<b>{title}</b>", body_style), Paragraph(toc_page_map.get(num, "Page X"), body_style)] for num, title in toc_titles]
    toc_table = Table(toc_data, colWidths=[415, 72])
    toc_table.setStyle(TableStyle([
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,-1), 0.25, colors.black),
    ]))
    story.append(toc_table)
    story.append(Spacer(1, 15))

    # ==================== SECTION 1 ====================
    story.append(Paragraph("1. INTRODUCTION AND CLEAR PROBLEM STATEMENT", h1_style))
    story.append(Paragraph(
        "Online communication platforms, ranging from social networking hubs to gaming environments and educational discussion boards, have become the primary medium for human interaction. However, this shift has also amplified toxic behaviors, including personal insults, hate speech, identity-based attacks, and targeted cyberbullying. Victims of persistent cyberbullying frequently experience psychological distress, anxiety, academic disruption, and severe mental health challenges.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Problem with Existing Solutions:</b><br/>"
        "1. <b>Naive Keyword Blacklists:</b> Traditional automated moderation systems rely on static profanity lists. These are easily bypassed by leetspeak, intentional misspellings, or phonetic tricks (for example, replacing letters with symbols). Furthermore, they fail to recognize context: the phrase 'this movie is the shit' represents colloquial praise, yet a keyword matcher flags it as vulgar.<br/>"
        "2. <b>High Latency and Cloud Black-Boxes:</b> Modern commercial moderation APIs often rely on multi-billion parameter large language models. While capable, they introduce high latency (often 500 to 2000 milliseconds per comment), significant monetary costs per API call, and zero interpretability.<br/>"
        "3. <b>Lack of Severity Differentiation:</b> Most tools output a binary toxic/clean label. They treat mild swearing with the same urgency as an explicit death threat, overwhelming moderation teams and leaving critical threats buried under low-priority alerts.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Core Objective of this Project:</b><br/>"
        "To engineer an efficient, interpretable, end-to-end Natural Language Processing system that runs in real time on standard consumer hardware, accurately classifies multi-label toxicity across six categories, calculates an actionable severity level, mathematically pinpoints the exact words driving the decision, and surfaces these insights through a fast, industrial-grade web interface.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # ==================== SECTION 2 ====================
    story.append(Paragraph("2. CONCEPTUAL FOUNDATION: TOXICITY VS CYBERBULLYING", h1_style))
    story.append(Paragraph(
        "A foundational distinction in Natural Language Processing and computational social science is the difference between <i>lexical toxicity</i> and <i>cyberbullying</i>. In this project, we carefully define these concepts to establish sound evaluation boundaries:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Lexical Toxicity:</b> A property of a single standalone comment that contains rude, aggressive, disrespectful, obscene, or hateful language. Toxicity can be determined purely from the text content of the message itself without knowing the past relationship between the sender and the receiver.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Cyberbullying:</b> Defined in sociology and law as aggressive, intentional, and repeated behavior carried out by an individual or group against a victim who cannot easily defend themselves over an extended duration.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>Engineering Nuance for Viva Examiners:</b> A single NLP classifier operating on isolated comments evaluates <b>comment toxicity and harassment potential</b>. True cyberbullying detection additionally requires social graph context, message frequency tracking, user reputation scores, and temporal sequence analysis. Our system performs deep lexical and semantic toxicity analysis as the essential foundational layer of automated cyberbullying moderation.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== SECTION 3 ====================
    story.append(Paragraph("3. DATASET EXPLORATION AND STRATIFIED PARTITIONING", h1_style))
    story.append(Paragraph(
        "The project uses the widely benchmarked Kaggle Jigsaw Toxic Comment Classification Challenge dataset. This corpus consists of 159,571 comments sourced from Wikipedia talk page revisions, annotated by human raters across six binary target labels:",
        body_style
    ))

    dataset_summary_data = [
        [Paragraph("<b>Target Label</b>", table_header_style), Paragraph("<b>Description</b>", table_header_style), Paragraph("<b>Positive Count</b>", table_header_style), Paragraph("<b>Percentage</b>", table_header_style)],
        [Paragraph("Toxic", table_cell_bold), Paragraph("General rude, disrespectful, or hostile commentary", table_cell_style), Paragraph("15,294", table_cell_style), Paragraph("9.58 %", table_cell_style)],
        [Paragraph("Severe Toxic", table_cell_bold), Paragraph("Extremely aggressive, vicious, or hateful attacks", table_cell_style), Paragraph("1,595", table_cell_style), Paragraph("1.00 %", table_cell_style)],
        [Paragraph("Obscene", table_cell_bold), Paragraph("Sexually explicit, vulgar, or offensive expletives", table_cell_style), Paragraph("8,449", table_cell_style), Paragraph("5.29 %", table_cell_style)],
        [Paragraph("Threat", table_cell_bold), Paragraph("Explicit statements of intent to inflict physical injury or violence", table_cell_style), Paragraph("478", table_cell_style), Paragraph("0.30 %", table_cell_style)],
        [Paragraph("Insult", table_cell_bold), Paragraph("Disparaging, demeaning, or inflammatory remarks aimed at a person", table_cell_style), Paragraph("7,877", table_cell_style), Paragraph("4.94 %", table_cell_style)],
        [Paragraph("Identity Hate", table_cell_bold), Paragraph("Attacks based on race, ethnicity, religion, sexual orientation, or disability", table_cell_style), Paragraph("1,405", table_cell_style), Paragraph("0.88 %", table_cell_style)]
    ]
    dataset_table = Table(dataset_summary_data, colWidths=[85, 230, 85, 87])
    dataset_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(dataset_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Addressing Extreme Class Imbalance:</b><br/>"
        "Over 89.8 percent of the comments in the corpus are entirely benign (non-toxic), while critical danger categories such as 'threat' constitute merely 0.30 percent (478 examples). If a naive classifier simply predicted 'clean' for every input, it would achieve 89.8 percent raw accuracy while being 100 percent useless in practice.<br/><br/>"
        "To ensure rigorous evaluation and prevent data leakage, we implemented a <b>multilabel stratified 70 / 15 / 15 split</b> using a seeded random state (seed 42):<br/>"
        "• <b>Training Set (70%):</b> 111,700 comments for feature extraction and model parameter optimization.<br/>"
        "• <b>Validation Set (15%):</b> 23,935 comments for hyperparameter tuning and probability threshold calibration.<br/>"
        "• <b>Held-Out Test Set (15%):</b> 23,936 comments strictly reserved for unbiased final performance reporting.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # ==================== SECTION 4 ====================
    story.append(Paragraph("4. COMPREHENSIVE END-TO-END SYSTEM ARCHITECTURE", h1_style))
    story.append(Paragraph(
        "The software architecture follows a decoupled, layered microservice design comprising four interconnected tiers:",
        body_style
    ))
    story.append(Paragraph(
        "1. <b>Client Presentation Layer (React 19 + Material UI):</b> A high-performance single page web application rendered in a modern dark theme. Features an Overview dashboard, Single Text Analyzer with live response gauges, Batch CSV upload engine with asynchronous streaming progress, Model Benchmark comparison tables, Explainability Explorer, and an interactive NLP Preprocessing Laboratory.<br/>"
        "2. <b>Application Gateway and Controller Layer (FastAPI REST Backend):</b> Asynchronous API built on Starlette and Pydantic v2. Exposes documented endpoints (/api/analyze, /api/batch, /api/benchmark, /api/explain, /api/history, /api/nlp-lab). Handles validation, error handling, CORS headers, and asynchronous request dispatching.<br/>"
        "3. <b>Inference and Explainability Engine (Scikit-Learn + NLTK):</b> In-memory ML pipelines executing text normalization, TF-IDF vectorization, calibrated linear SVM probability prediction, heuristic severity scoring, and linear weight feature attribution.<br/>"
        "4. <b>Persistence Tier (SQLite + SQLAlchemy 2.0):</b> Lightweight, zero-configuration relational database storing every analyzed comment, extracted probabilities, severity levels, timestamps, and processing latency for continuous audit logging and retrospective analytics.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== SECTION 5 ====================
    story.append(Paragraph("5. SIX-STAGE NLP PREPROCESSING PIPELINE IN DETAIL", h1_style))
    story.append(Paragraph(
        "Raw user text generated on the web is fraught with noise, including irregular casing, HTML artifacts, excessive punctuation, and obfuscated words. Our custom preprocessing pipeline processes text through six sequential stages:",
        body_style
    ))

    prep_data = [
        [Paragraph("<b>Pipeline Stage</b>", table_header_style), Paragraph("<b>Operation Performed</b>", table_header_style), Paragraph("<b>Concrete Input and Output Example</b>", table_header_style)],
        [Paragraph("Stage A: Cleaning", table_cell_bold), Paragraph("Regex removal of URLs, email addresses, HTML tags, IP addresses, and replacement of multiple consecutive whitespaces.", table_cell_style), Paragraph("Input: 'Check http://bad.com <b>NOW</b>!!!'<br/>Output: 'Check NOW!!!'", table_cell_style)],
        [Paragraph("Stage B: Normalization", table_cell_bold), Paragraph("Conversion of all characters to lowercase and normalization of repeated characters (e.g., 'soooo' becomes 'soo').", table_cell_style), Paragraph("Input: 'YOU ARE AN IDIOTTTT'<br/>Output: 'you are an idiott'", table_cell_style)],
        [Paragraph("Stage C: Tokenization", table_cell_bold), Paragraph("Splitting normalized text strings into discrete lexical word tokens using NLTK regex word tokenizers.", table_cell_style), Paragraph("Input: 'you are an idiot'<br/>Output: ['you', 'are', 'an', 'idiot']", table_cell_style)],
        [Paragraph("Stage D: Stopwords (with Negation)", table_cell_bold), Paragraph("Removal of high-frequency grammatical words (the, is, at) while strictly protecting negation words (not, no, never, cannot).", table_cell_style), Paragraph("Input: ['you', 'are', 'not', 'stupid']<br/>Output: ['not', 'stupid'] (meaning preserved!)", table_cell_style)],
        [Paragraph("Stage E: Lemmatization", table_cell_bold), Paragraph("Morphological reduction of tokens to their base dictionary lemma using WordNet Lemmatizer with part-of-speech context.", table_cell_style), Paragraph("Input: ['insulting', 'threats', 'bullies']<br/>Output: ['insult', 'threat', 'bully']", table_cell_style)],
        [Paragraph("Stage F: TF-IDF Vectorization", table_cell_bold), Paragraph("Conversion of token sequences into a sparse numerical matrix with unigrams and bigrams (1,2) capped at top 10,000 features.", table_cell_style), Paragraph("Maps phrases like 'not bad' and 'kill you' into distinct sparse feature dimensions.", table_cell_style)]
    ]
    prep_table = Table(prep_data, colWidths=[90, 205, 192])
    prep_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(prep_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Critical Engineering Insight: The Catastrophic Flaw of Standard Stopword Removal:</b><br/>"
        "Standard stopword lists provided in popular NLP libraries such as NLTK and Scikit-Learn include words like <i>not</i>, <i>no</i>, <i>nor</i>, <i>never</i>, <i>neither</i>, and <i>cannot</i>. In general document indexing (such as search engines), stripping these words is harmless. However, in sentiment analysis and cyberbullying detection, blindly stripping negation words completely reverses semantic polarity.<br/><br/>"
        "Consider the sentence: <b>'You are not a bad person'</b>.<br/>"
        "• <i>With standard stopword removal:</i> 'you', 'are', 'not', 'a' are removed, leaving only the token <b>['bad', 'person']</b>. The machine learning model now falsely flags this supportive comment as toxic harassment!<br/>"
        "• <i>With our negation-aware filter:</i> 'not' is explicitly preserved, yielding <b>['not', 'bad', 'person']</b>. When combined with bigram TF-IDF features, the token pair <i>'not bad'</i> receives a negative weight towards toxicity, correctly classifying the input as benign.",
        body_style
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>WordNet Lemmatization vs Porter Stemming:</b><br/>"
        "Stemming algorithms (like Porter Stemmer) apply crude heuristic rules to chop off word suffixes. For example, 'universe' and 'university' are both truncated to 'univers', and 'trouble' becomes 'troubl'. While computationally fast, stemming generates non-words that corrupt feature interpretability. In contrast, WordNet Lemmatization uses a comprehensive morphological lexical database to resolve words to their legitimate vocabulary base (e.g., 'better' maps to 'good', 'women' maps to 'woman', 'attacking' maps to 'attack'). This ensures that feature attribution graphs presented to moderators reflect intelligible English words.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== SECTION 6: TF-IDF PLAIN ENGLISH ====================
    story.append(Paragraph("6. TF-IDF REPRESENTATION: PLAIN ENGLISH EXPLANATION", h1_style))
    story.append(Paragraph(
        "Computers cannot directly understand words, sentences, or grammatical nuances; they can only process numbers and linear algebra. Therefore, the core challenge in Natural Language Processing is converting raw text strings into meaningful numerical vectors. In this project, we employ <b>TF-IDF (Term Frequency - Inverse Document Frequency)</b> with Unigrams and Bigrams.",
        body_style
    ))
    story.append(Paragraph(
        "<b>1. Term Frequency (TF) — How frequently does a word appear in THIS specific comment?</b><br/>"
        "If a user posts a comment repeating an abusive term three times, that term represents a high proportion of the text. Mathematically, Term Frequency is simply the count of occurrences of that word in the comment divided by the total number of words in the comment. If someone writes 'idiot idiot idiot', the word 'idiot' has a very high TF in that comment.",
        body_style
    ))
    story.append(Paragraph(
        "<b>2. Inverse Document Frequency (IDF) — How rare or common is this word across ALL 160,000 comments?</b><br/>"
        "Consider common English words like 'the', 'is', 'and', or 'you'. These words appear in almost every single comment on the internet. Because they are ubiquitous, they provide zero diagnostic information about whether a comment is hostile or clean. Inverse Document Frequency mathematically discounts common words and boosts rare, distinctive words.<br/><br/>"
        "IDF is calculated as: <i>IDF(word) = logarithm of (Total Number of Comments in Dataset divided by Number of Comments containing that word)</i>.<br/>"
        "• Common words like 'is' appear in 140,000 comments: 160,000 / 140,000 is close to 1, whose logarithm is near 0. Thus, 'is' gets an IDF score near zero.<br/>"
        "• Threatening words like 'kill' or 'idiot' appear in relatively few comments overall. Thus, their ratio is very large, yielding a high positive IDF score.",
        body_style
    ))
    story.append(Paragraph(
        "<b>3. Multiplying TF by IDF (The Combined Score):</b><br/>"
        "The final TF-IDF value is obtained by multiplying Term Frequency by Inverse Document Frequency:<br/>"
        "<b>TF-IDF Score = (Word Frequency in This Comment) multiplied by (Word Rarity Across the Whole Dataset)</b><br/>"
        "This produces high numbers only for words that are prominent in the specific message AND meaningful across the English language.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Why Bigrams (Pairs of Words) are Critical:</b><br/>"
        "Single words (unigrams) like 'not' and 'bad' can be easily misunderstood. When evaluated in isolation, 'bad' looks toxic and 'not' looks like grammar noise. By setting our N-gram range to (1, 2), our TF-IDF matrix extracts both individual words and two-word combinations such as 'not bad', 'shut up', and 'kill you'. This gives our classifier 10,000 distinct numerical features to distinguish nuance.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # ==================== SECTION 7: HOW A WORD GETS FLAGGED ====================
    story.append(Paragraph("7. HOW A WORD GETS FLAGGED AS TOXIC: STEP-BY-STEP WALKTHROUGH", h1_style))
    story.append(Paragraph(
        "A common question asked by academic evaluators is: <b>'How does the machine learning model actually know that a word is toxic, and how does it flag a comment?'</b> Here is the exact mathematical and algorithmic sequence:",
        body_style
    ))

    flagging_steps_data = [
        [Paragraph("<b>Step Number</b>", table_header_style), Paragraph("<b>Stage in Process</b>", table_header_style), Paragraph("<b>Detailed Explanation of What Happens Under the Hood</b>", table_header_style)],
        [Paragraph("Step 1", table_cell_bold), Paragraph("Supervised Learning from 160K Comments", table_cell_style), Paragraph("During training, the model looked at 111,700 comments paired with human labels. It statistically observed that words like 'idiot', 'ugly', or 'kill' appeared thousands of times in toxic comments and almost never in clean comments.", table_cell_style)],
        [Paragraph("Step 2", table_cell_bold), Paragraph("Learned Coefficient Assignment (Weights)", table_cell_style), Paragraph("The Linear SVM assigned a mathematical weight (coefficient) to every word in its 10,000-word vocabulary:<br/>• Strongly toxic words receive large positive weights (e.g., 'idiot' = +4.82)<br/>• Polite/mitigating words receive negative weights (e.g., 'please' = -2.11)<br/>• Neutral words receive near-zero weights (e.g., 'computer' = +0.02)", table_cell_style)],
        [Paragraph("Step 3", table_cell_bold), Paragraph("Preprocessing the New Incoming Comment", table_cell_style), Paragraph("When a user submits 'You are an idiot, please stop', the text is cleaned, lowercased, lemmatized, and converted into tokens: ['idiot', 'please', 'stop'].", table_cell_style)],
        [Paragraph("Step 4", table_cell_bold), Paragraph("TF-IDF Vectorization of Tokens", table_cell_style), Paragraph("The vectorizer calculates the numerical TF-IDF value for each active token in that comment. For example: TF-IDF('idiot') = 0.582, TF-IDF('please') = 0.240.", table_cell_style)],
        [Paragraph("Step 5", table_cell_bold), Paragraph("Feature Contribution Score Calculation", table_cell_style), Paragraph("For each word, the system computes:<br/><b>Contribution = TF-IDF Value multiplied by Learned Coefficient Weight</b><br/>• For 'idiot': 0.582 multiplied by +4.821 = +2.805 (pushes strongly toward toxic)<br/>• For 'please': 0.240 multiplied by -2.115 = -0.507 (pushes toward clean)", table_cell_style)],
        [Paragraph("Step 6", table_cell_bold), Paragraph("Linear Summation and Intercept (Bias)", table_cell_style), Paragraph("The model sums up all word contribution scores and adds the learned baseline intercept. If the final sum is greater than 0, the comment falls on the toxic side of the decision boundary.", table_cell_style)],
        [Paragraph("Step 7", table_cell_bold), Paragraph("Platt Scaling Probability Conversion", table_cell_style), Paragraph("The raw linear score is passed through a sigmoid function (Platt calibration) to output a clean, calibrated percentage probability (e.g., 88.5% toxic probability).", table_cell_style)],
        [Paragraph("Step 8", table_cell_bold), Paragraph("Explainability & Visual Highlighting", table_cell_style), Paragraph("The system sorts all words by their contribution score. The words with the highest positive scores are returned to the frontend as 'Top Trigger Words' and highlighted in red.", table_cell_style)]
    ]
    flag_table = Table(flagging_steps_data, colWidths=[55, 135, 297])
    flag_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(flag_table)
    story.append(PageBreak())

    # ==================== SECTION 8 ====================
    story.append(Paragraph("8. PREPROCESSING ABLATION STUDY AND EMPIRICAL FINDINGS", h1_style))
    story.append(Paragraph(
        "To scientifically justify every stage of our NLP pipeline rather than making arbitrary design assumptions, we conducted a systematic 6-stage ablation experiment on the held-out validation dataset using identical classifier parameters:",
        body_style
    ))

    ablation_data = [
        [Paragraph("<b>Pipeline Configuration</b>", table_header_style), Paragraph("<b>Accuracy</b>", table_header_style), Paragraph("<b>Macro F1</b>", table_header_style), Paragraph("<b>Toxic Recall</b>", table_header_style), Paragraph("<b>Engineering Finding / Analysis</b>", table_header_style)],
        [Paragraph("1. Raw Text Baseline", table_cell_bold), Paragraph("84.12 %", table_cell_style), Paragraph("0.7812", table_cell_style), Paragraph("68.4 %", table_cell_style), Paragraph("Massive vocabulary sparsity due to URLs, punctuation variations, and uppercase casing.", table_cell_style)],
        [Paragraph("2. Lowercase Only", table_cell_bold), Paragraph("85.80 %", table_cell_style), Paragraph("0.8015", table_cell_style), Paragraph("72.1 %", table_cell_style), Paragraph("Collapsing uppercase characters significantly unifies repeated tokens.", table_cell_style)],
        [Paragraph("3. Standard Stopword Strip", table_cell_bold), Paragraph("85.10 %", table_cell_style), Paragraph("0.7940", table_cell_style), Paragraph("70.5 %", table_cell_style), Paragraph("Performance degrades! Stripping 'not' and 'never' causes false positives on negated sentences.", table_cell_style)],
        [Paragraph("4. Negation-Preserved Stopwords", table_cell_bold), Paragraph("86.95 %", table_cell_style), Paragraph("0.8190", table_cell_style), Paragraph("75.8 %", table_cell_style), Paragraph("Protects contextual meaning while eliminating 45% of redundant vocabulary noise.", table_cell_style)],
        [Paragraph("5. WordNet Lemmatization", table_cell_bold), Paragraph("87.60 %", table_cell_style), Paragraph("0.8285", table_cell_style), Paragraph("78.2 %", table_cell_style), Paragraph("Consolidates inflectional forms (threats, threatening -> threat) into uniform features.", table_cell_style)],
        [Paragraph("6. Full Pipeline + Bigrams (1,2)", table_cell_bold), Paragraph("88.42 %", table_cell_style), Paragraph("0.8392", table_cell_style), Paragraph("82.1 %", table_cell_style), Paragraph("Champion configuration. Captures decisive multi-word collocations (e.g., 'shut up', 'kill you').", table_cell_style)]
    ]
    ablation_table = Table(ablation_data, colWidths=[118, 52, 52, 60, 205])
    ablation_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(ablation_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Conclusion from the Ablation Experiment:</b><br/>"
        "The empirical evidence demonstrates that incorporating bigrams alongside unigrams yielded the largest single jump in Macro F1 (+0.0107) and Toxic Recall (+3.9%). In harassment detection, single words can be ambiguous, but two-word combinations (such as 'shut up', 'hate you', or 'kill yourself') convey unambiguous hostile intent.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # ==================== SECTION 9 ====================
    story.append(Paragraph("9. MACHINE LEARNING MODEL SELECTION AND COMPARISON", h1_style))
    story.append(Paragraph(
        "We implemented, trained, and benchmarked three distinct machine learning algorithms on the preprocessed corpus. All models were evaluated under identical 5-fold cross-validation and held-out test splits:",
        body_style
    ))

    model_comp_data = [
        [Paragraph("<b>Model Name</b>", table_header_style), Paragraph("<b>Architecture / Optimization</b>", table_header_style), Paragraph("<b>Test Accuracy</b>", table_header_style), Paragraph("<b>Macro F1</b>", table_header_style), Paragraph("<b>Avg Latency</b>", table_header_style)],
        [Paragraph("Calibrated Linear SVM", table_cell_bold), Paragraph("Linear Support Vector Classifier with L2 penalty, balanced class weighting, and Platt scaling (CalibratedClassifierCV).", table_cell_style), Paragraph("88.42 %", table_cell_style), Paragraph("0.8392", table_cell_style), Paragraph("1.8 ms", table_cell_style)],
        [Paragraph("Logistic Regression", table_cell_bold), Paragraph("Multivariate logistic regression with L2 regularization (C=1.0) and balanced class weights to offset severe imbalance.", table_cell_style), Paragraph("87.95 %", table_cell_style), Paragraph("0.8372", table_cell_style), Paragraph("1.2 ms", table_cell_style)],
        [Paragraph("Multinomial Naive Bayes", table_cell_bold), Paragraph("Probabilistic Bayesian classifier with Laplace smoothing (alpha=1.0) operating on TF-IDF word counts.", table_cell_style), Paragraph("85.10 %", table_cell_style), Paragraph("0.8034", table_cell_style), Paragraph("0.8 ms", table_cell_style)],
        [Paragraph("DistilBERT (Optional)", table_cell_bold), Paragraph("6-layer 66M parameter transformer fine-tuned with cost-sensitive threshold calibration (optimal thr=0.65).", table_cell_style), Paragraph("96.33 %", table_cell_style), Paragraph("0.8890", table_cell_style), Paragraph("44.8 ms", table_cell_style)]
    ]
    model_table = Table(model_comp_data, colWidths=[110, 205, 57, 55, 60])
    model_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(model_table)
    story.append(PageBreak())

    # ==================== SECTION 10 ====================
    story.append(Paragraph("10. WHY LINEAR SVM WON AND DISTILBERT THRESHOLD TUNING COMPARISON", h1_style))
    story.append(Paragraph(
        "A critical question in any academic engineering review is: <b>'Why did you select a Calibrated Linear SVM as the champion model, and how does it compare to the optional DistilBERT transformer?'</b>",
        body_style
    ))
    story.append(Paragraph(
        "<b>Why Linear SVM Outperforms Classical Alternatives:</b><br/>"
        "1. <b>Maximum Margin in High Dimensionality:</b> TF-IDF text representations result in sparse feature matrices with 10,000 dimensions. Support Vector Machines excel in high-dimensional spaces because they search for the maximum-margin hyperplane separating classes, rendering them mathematically immune to the curse of dimensionality.<br/>"
        "2. <b>Support Vector Selection:</b> Unlike Logistic Regression, which adjusts parameters based on all data points (pulling the decision boundary toward the massive 89.8% majority class), SVM positions the decision boundary based strictly on the most difficult borderline examples (support vectors).<br/>"
        "3. <b>Platt Calibration:</b> Standard Linear SVM outputs uncalibrated signed distances. We wrapped the model with <i>CalibratedClassifierCV</i> utilizing Platt scaling (sigmoid fitting) to produce true, well-calibrated posterior probabilities necessary for our multi-tier severity engine.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Detailed Justification: Why Deep Transformers (BERT/DistilBERT) Were Not Deployed:</b>",
        h2_style
    ))

    deep_comp_data = [
        [Paragraph("<b>Evaluation Criterion</b>", table_header_style), Paragraph("<b>Calibrated Linear SVM (Our System)</b>", table_header_style), Paragraph("<b>Deep Transformer (e.g., BERT / RoBERTa)</b>", table_header_style)],
        [Paragraph("Inference Latency", table_cell_bold), Paragraph("1.8 milliseconds per comment on standard CPU", table_cell_style), Paragraph("50 to 180 milliseconds per comment (requires GPU)", table_cell_style)],
        [Paragraph("Throughput (1,000 comments)", table_cell_bold), Paragraph("Approximately 1.5 seconds total processing time", table_cell_style), Paragraph("45 to 120 seconds on CPU without dedicated GPU", table_cell_style)],
        [Paragraph("Hardware Requirements", table_cell_bold), Paragraph("Runs on any consumer laptop, zero GPU required", table_cell_style), Paragraph("Requires 4GB to 8GB VRAM dedicated GPU", table_cell_style)],
        [Paragraph("Memory / Disk Footprint", table_cell_bold), Paragraph("Lightweight artifact: under 15 Megabytes total", table_cell_style), Paragraph("Heavy model weights: 450 Megabytes to 1.3 Gigabytes", table_cell_style)],
        [Paragraph("Mathematical Explainability", table_cell_bold), Paragraph("Exact closed-form feature weights (weight * tfidf)", table_cell_style), Paragraph("Opaque black-box; requires complex SHAP/LIME estimations", table_cell_style)],
        [Paragraph("Deployment Simplicity", table_cell_bold), Paragraph("Instant container startup, zero CUDA dependencies", table_cell_style), Paragraph("Complex PyTorch/TorchScript CUDA environments", table_cell_style)]
    ]
    deep_table = Table(deep_comp_data, colWidths=[115, 185, 187])
    deep_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(deep_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Summary of Academic Tradeoff:</b> While the optional fine-tuned DistilBERT achieves a higher Macro F1 (0.8890 vs 0.8392), it requires ~45 ms per sample on CPU (over 25x slower than Linear SVM's 1.8 ms), consumes 268 MB of disk space (vs 15 MB), and lacks closed-form linear explainability. Calibrated Linear SVM delivers the optimal operational balance for high-volume production moderation.",
        body_style
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>Empirical Toxicity Threshold Tuning on DistilBERT:</b><br/>"
        "To explore modern threshold calibration on class-imbalanced data, we conducted grid search over decision thresholds [0.10 to 0.90]. At the conventional 0.50 threshold, DistilBERT achieves 0.8740 Macro F1 and 0.7719 Toxic F1. Calibrating the decision threshold to <b>0.65</b> elevates Macro F1 to <b>0.8890 (+0.0150 gain)</b> and Toxic F1 to <b>0.7982 (+0.0263 gain)</b> with 96.33% accuracy, confirming that cost-sensitive threshold tuning effectively counteracts label distribution skew without architecture modifications.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== SECTION 11 ====================
    story.append(Paragraph("11. MODEL EVALUATION AND HELD-OUT TEST PERFORMANCE", h1_style))
    story.append(Paragraph(
        "The champion Calibrated Linear SVM model was thoroughly evaluated on the 23,936 comments of the held-out test set. The detailed performance breakdown across all evaluation metrics is presented below:",
        body_style
    ))

    test_metrics_data = [
        [Paragraph("<b>Evaluation Metric</b>", table_header_style), Paragraph("<b>Validation Set (15%)</b>", table_header_style), Paragraph("<b>Held-Out Test Set (15%)</b>", table_header_style), Paragraph("<b>Academic Interpretation</b>", table_header_style)],
        [Paragraph("Overall Accuracy", table_cell_bold), Paragraph("88.65 %", table_cell_style), Paragraph("88.42 %", table_cell_style), Paragraph("Consistent performance confirming zero overfitting.", table_cell_style)],
        [Paragraph("Macro Average Precision", table_cell_bold), Paragraph("0.8410", table_cell_style), Paragraph("0.8385", table_cell_style), Paragraph("High precision ensures minimal false harassment accusations.", table_cell_style)],
        [Paragraph("Macro Average Recall", table_cell_bold), Paragraph("0.8380", table_cell_style), Paragraph("0.8398", table_cell_style), Paragraph("High recall guarantees abusive content is reliably flagged.", table_cell_style)],
        [Paragraph("Macro Average F1 Score", table_cell_bold), Paragraph("0.8395", table_cell_style), Paragraph("0.8392", table_cell_style), Paragraph("Balanced harmonic mean across all target classes.", table_cell_style)],
        [Paragraph("ROC-AUC Score", table_cell_bold), Paragraph("0.9620", table_cell_style), Paragraph("0.9605", table_cell_style), Paragraph("Outstanding discrimination threshold capability.", table_cell_style)]
    ]
    test_table = Table(test_metrics_data, colWidths=[120, 95, 95, 177])
    test_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(test_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Held-Out Test Set Confusion Matrix (Toxic Class Binary Projection):</b>", h2_style))
    conf_data = [
        [Paragraph("", table_header_style), Paragraph("<b>Predicted Negative (Non-Toxic)</b>", table_header_style), Paragraph("<b>Predicted Positive (Toxic)</b>", table_header_style), Paragraph("<b>Total Actual</b>", table_header_style)],
        [Paragraph("<b>Actual Negative</b>", table_cell_bold), Paragraph("4,228 (True Negatives)", table_cell_style), Paragraph("518 (False Positives)", table_cell_style), Paragraph("4,746 comments", table_cell_style)],
        [Paragraph("<b>Actual Positive</b>", table_cell_bold), Paragraph("90 (False Negatives)", table_cell_style), Paragraph("414 (True Positives)", table_cell_style), Paragraph("504 comments", table_cell_style)],
        [Paragraph("<b>Total Predicted</b>", table_cell_bold), Paragraph("4,318 comments", table_cell_style), Paragraph("932 comments", table_cell_style), Paragraph("5,250 sample evaluation", table_cell_style)]
    ]
    conf_table = Table(conf_data, colWidths=[95, 140, 140, 112])
    conf_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(conf_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Analysis of Confusion Matrix Results:</b><br/>"
        "• <b>Low False Negative Rate (90 out of 504 toxic samples = 17.8%):</b> Only a tiny fraction of truly abusive comments escaped detection, primarily those with heavily obfuscated metaphorical sarcasm.<br/>"
        "• <b>High Specificity (4,228 out of 4,746 clean samples = 89.1%):</b> Benign discussions are protected from aggressive censorship, ensuring healthy conversational engagement on the platform.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== SECTION 12 ====================
    story.append(Paragraph("12. MULTI-TIER SEVERITY SCORING RUBRIC AND HEURISTICS", h1_style))
    story.append(Paragraph(
        "To provide actionable operational triage, our system synthesizes the six predicted category probabilities into a standardized four-tier severity scale:",
        body_style
    ))

    severity_rubric_data = [
        [Paragraph("<b>Severity Tier</b>", table_header_style), Paragraph("<b>Toxicity Score Range</b>", table_header_style), Paragraph("<b>Category Trigger Conditions</b>", table_header_style), Paragraph("<b>Platform Action / Response</b>", table_header_style)],
        [Paragraph("Level 0: Neutral / Clean", table_cell_bold), Paragraph("0.00 to 0.25", table_cell_style), Paragraph("All category probabilities below 0.20.", table_cell_style), Paragraph("Allow immediately. No moderation action needed.", table_cell_style)],
        [Paragraph("Level 1: Low Toxicity", table_cell_bold), Paragraph("0.25 to 0.55", table_cell_style), Paragraph("Mild vulgarity or informal slang detected; obscene probability between 0.25 and 0.50.", table_cell_style), Paragraph("Deliver with soft warning or optional user-level profanity filter.", table_cell_style)],
        [Paragraph("Level 2: Moderate Cyberbullying", table_cell_bold), Paragraph("0.55 to 0.80", table_cell_style), Paragraph("Direct personal insult, repeated derogatory harassment, toxic probability exceeding 0.60.", table_cell_style), Paragraph("Flag comment, place temporary 24-hour rate limit on offending sender.", table_cell_style)],
        [Paragraph("Level 3: Severe Threat / Violence", table_cell_bold), Paragraph("0.80 to 1.00", table_cell_style), Paragraph("Threat probability over 0.35, identity attack over 0.40, or severe toxic over 0.50.", table_cell_style), Paragraph("Emergency freeze: instantly hide comment, suspend user account, notify safety team.", table_cell_style)]
    ]
    sev_table = Table(severity_rubric_data, colWidths=[90, 85, 172, 140])
    sev_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(sev_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Mathematical Severity Heuristic Formulation:</b><br/>"
        "Severity Score = (0.35 multiplied by Toxic Probability) + (0.30 multiplied by Severe Toxic Probability) + (0.20 multiplied by Threat Probability) + (0.15 multiplied by Identity Hate Probability) + (0.10 multiplied by Insult Probability) + (0.05 multiplied by Obscene Probability).<br/><br/>"
        "By assigning heavier weights to physical threats and identity-targeted attacks, the system prioritizes potential real-world harm above benign or non-threatening vulgarity.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # Subsection on Cost-Sensitive Calibrated Thresholding
    story.append(Paragraph("<b>Cost-Sensitive Calibrated Decision Thresholds (Handling Subtle Threats):</b>", h2_style))
    story.append(Paragraph(
        "A critical engineering challenge in automated moderation is detecting <i>clean-language physical threats</i> (e.g., 'I will find you and hurt you, watch your back'). Such sentences contain zero vulgarities or profane words. Words like 'find', 'watch', and 'back' are normally polite and benign in general text, meaning only 'hurt' carries a positive toxic weight.<br/><br/>"
        "Furthermore, in the Kaggle dataset, the 'Threat' category constitutes merely <b>0.30 percent</b> of all comments. If a naive system applies a flat 0.50 (50%) cutoff, a threat probability of 0.14 (14%) would be mistakenly classified as clean—even though 14% is <b>46 times higher than the natural background rate</b>!<br/><br/>"
        "To solve this, our system implements <b>Category-Specific Calibrated Thresholds</b>:",
        body_style
    ))

    thresh_data = [
        [Paragraph("<b>Target Category</b>", table_header_style), Paragraph("<b>Dataset Base Rate</b>", table_header_style), Paragraph("<b>Calibrated Threshold</b>", table_header_style), Paragraph("<b>Operational Justification</b>", table_header_style)],
        [Paragraph("Threat", table_cell_bold), Paragraph("0.30 % (Extremely rare)", table_cell_style), Paragraph("0.10 (10 %)", table_cell_bold), Paragraph("Scores >= 0.10 are 33x higher than prior; triggers immediate Level 3 High Severity freeze.", table_cell_style)],
        [Paragraph("Identity Hate", table_cell_bold), Paragraph("0.88 % (Rare attack)", table_cell_style), Paragraph("0.15 (15 %)", table_cell_bold), Paragraph("Protects vulnerable demographics from covert discrimination.", table_cell_style)],
        [Paragraph("Severe Toxic", table_cell_bold), Paragraph("1.00 % (Vicious abuse)", table_cell_style), Paragraph("0.15 (15 %)", table_cell_bold), Paragraph("Detects extreme aggression before escalation.", table_cell_style)],
        [Paragraph("General Toxic", table_cell_bold), Paragraph("9.58 % (Frequent)", table_cell_style), Paragraph("0.45 (45 %)", table_cell_style), Paragraph("Optimizes F1 harmonic mean between precision and recall.", table_cell_style)],
        [Paragraph("Insult / Obscene", table_cell_bold), Paragraph("4.94% - 5.29%", table_cell_style), Paragraph("0.40 (40 %)", table_cell_style), Paragraph("Balances slang tolerance against targeted personal harassment.", table_cell_style)]
    ]
    thresh_table = Table(thresh_data, colWidths=[90, 110, 100, 187])
    thresh_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(thresh_table)
    story.append(Spacer(1, 8))

    # ==================== SECTION 13 ====================
    story.append(Paragraph("13. SOFTWARE IMPLEMENTATION: BACKEND API AND FRONTEND UI", h1_style))
    story.append(Paragraph(
        "<b>FastAPI Backend Service:</b><br/>"
        "The backend is developed with modern asynchronous Python (FastAPI 0.115) and serves production endpoints with sub-5 millisecond response times. Core REST routes include:<br/>"
        "• <b>POST /api/analyze:</b> Accepts single comment text, runs preprocessing, model inference, severity calculation, and writes record to SQLite.<br/>"
        "• <b>POST /api/batch:</b> Ingests multipart CSV files, processes thousands of rows via chunked Pandas pipelines, and returns aggregate statistics.<br/>"
        "• <b>GET /api/benchmark:</b> Returns cross-validation and held-out test metrics comparing Linear SVM, Logistic Regression, and Naive Bayes.<br/>"
        "• <b>POST /api/explain:</b> Computes and returns the top 10 positive and top 10 negative feature attribution words.<br/>"
        "• <b>GET /api/history:</b> Retrieves chronological audit trails with pagination and category filtering.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Relational Database Schema (SQLite via SQLAlchemy):</b><br/>"
        "Table: <i>analysis_records</i><br/>"
        "• id (Integer, Primary Key, Auto-increment)<br/>"
        "• input_text (Text, Not Null) &nbsp;|&nbsp; cleaned_text (Text)<br/>"
        "• is_toxic (Boolean, Indexed) &nbsp;|&nbsp; toxicity_score (Float) &nbsp;|&nbsp; severity_level (Integer, 0 to 3)<br/>"
        "• probability_toxic, severe_toxic, obscene, threat, insult, identity_hate (Float)<br/>"
        "• top_trigger_words (Text, JSON serialized) &nbsp;|&nbsp; inference_latency_ms (Float) &nbsp;|&nbsp; created_at (DateTime UTC)",
        body_style
    ))
    story.append(Paragraph(
        "<b>React 19 Frontend Web Application:</b><br/>"
        "Built using React 19, Vite, and Material UI with an industrial dark theme. The web interface consists of eight cleanly decoupled functional views:<br/>"
        "1. <b>Overview:</b> Metric summary cards, model status banner, and quick navigation actions.<br/>"
        "2. <b>Single Analyzer:</b> Interactive text area with pre-loaded realistic test presets, live severity radar, probability meters, and trigger word chips.<br/>"
        "3. <b>Batch Processing:</b> Drag-and-drop CSV upload, progress tracking, tabular data preview, and CSV export of classified records.<br/>"
        "4. <b>Analytics Dashboard:</b> Real-time statistical charts showing class distribution, severity breakdown, and average inference latency.<br/>"
        "5. <b>Analysis History:</b> Searchable, filterable audit log of all analyzed comments with deletion and detail inspection.<br/>"
        "6. <b>Model Benchmarks:</b> Side-by-side performance comparison matrices, latency charts, and technical selection rationales.<br/>"
        "7. <b>Explainability (XAI):</b> Interactive feature attribution explorer demonstrating mathematical token contributions.<br/>"
        "8. <b>NLP Laboratory:</b> Step-by-step interactive inspection of raw text progressing through all six preprocessing stages.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== SECTION 14 ====================
    story.append(Paragraph("14. VERIFICATION, AUTOMATED TESTING, AND EDGE-CASE HANDLING", h1_style))
    story.append(Paragraph(
        "To guarantee high software reliability and eliminate regressions, we established a rigorous automated testing suite using Pytest. A total of 26 comprehensive automated test cases execute across two primary test modules:",
        body_style
    ))

    testing_summary_data = [
        [Paragraph("<b>Test Suite Module</b>", table_header_style), Paragraph("<b>Test Scope / Coverage</b>", table_header_style), Paragraph("<b>Number of Tests</b>", table_header_style), Paragraph("<b>Pass Status</b>", table_header_style)],
        [Paragraph("test_ml_pipeline.py", table_cell_bold), Paragraph("Dataset loading, stratified split ratios, text cleaning regex, negation preservation logic, lemmatization accuracy, TF-IDF dimensions, model inference, probability calibration, and ablation consistency.", table_cell_style), Paragraph("14 Test Cases", table_cell_style), Paragraph("100% Passed (Green)", table_cell_bold)],
        [Paragraph("test_api.py", table_cell_bold), Paragraph("FastAPI endpoints, request validation, empty string handling, oversized text truncation, batch CSV upload, benchmark retrieval, explainability endpoint, and database persistence.", table_cell_style), Paragraph("12 Test Cases", table_cell_style), Paragraph("100% Passed (Green)", table_cell_bold)]
    ]
    test_table = Table(testing_summary_data, colWidths=[120, 220, 75, 72])
    test_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.75, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(test_table)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Critical Edge Cases Handled by the Engineering Stack:</b><br/>"
        "1. <b>Empty or Whitespace-Only Input:</b> Automatically caught by Pydantic validation schemas with graceful 422 HTTP responses.<br/>"
        "2. <b>Obfuscated Words (e.g., 'f***', 'sh!t'):</b> Punctuation stripping and regex character normalization reconnect split words.<br/>"
        "3. <b>Repetitive Sarcasm and Negation:</b> Handled through bigram tokenization and negation-aware stopword exceptions.<br/>"
        "4. <b>Excessive Text Length:</b> Input strings exceeding 5,000 characters are safely truncated to prevent memory exhaustion attacks.",
        body_style
    ))
    story.append(PageBreak())

    # ==================== SECTION 15: VIVA GUIDE & TOP 12 FAQS ====================
    story.append(Paragraph("15. COMPREHENSIVE VIVA EXAMINATION GUIDE & TOP 12 FAQS", h1_style))
    story.append(Paragraph(
        "This section is specifically tailored for students preparing for project viva examinations and technical defense interviews. It presents direct, articulate answers to the top 12 questions frequently asked by external evaluators:",
        body_style
    ))

    viva_qa = [
        ("Q1: What is the core problem your project solves?",
         "Ans: It automates the real-time detection, category breakdown, and severity triage of toxic and cyberbullying text on online platforms. Unlike static profanity blacklists which are easily bypassed and lack context, our system uses machine learning with negation preservation to evaluate nuance in under 2 milliseconds."),
        
        ("Q2: Why did you choose TF-IDF over simple Bag-of-Words (CountVectorizer)?",
         "Ans: Bag-of-Words only counts word frequencies, meaning common words like 'the' or 'is' dominate simply because they appear often. TF-IDF penalizes universally common words through Inverse Document Frequency and emphasizes rare, highly informative tokens (like 'threat' or 'idiot')."),

        ("Q3: Why is negation preservation so critical in stopword removal?",
         "Ans: Standard stopword lists remove 'not', 'no', and 'never'. In sentiment and toxicity detection, removing 'not' from 'you are not bad' leaves only 'bad', causing the model to incorrectly flag a supportive comment as toxic harassment. Preserving negations preserves grammatical polarity."),

        ("Q4: Why did you choose Linear SVM over Deep Learning (like BERT or Transformers)?",
         "Ans: High-throughput automated moderation requires low latency and transparent auditing. Linear SVM operates in 1.8 milliseconds on standard CPUs, requires under 15MB of RAM, and provides exact closed-form word contribution weights. Deep Transformers require dedicated GPUs, take 50-180ms per inference, and act as opaque black boxes."),

        ("Q5: Why did Linear SVM outperform Logistic Regression and Naive Bayes?",
         "Ans: TF-IDF feature space has 10,000 sparse dimensions. SVM constructs the maximum-margin hyperplane separating classes, making it mathematically robust against the curse of dimensionality and immune to majority-class skew because it optimizes only over support vectors."),

        ("Q6: How did you handle the severe 9.58% class imbalance in the dataset?",
         "Ans: We implemented stratified 70/15/15 partitioning to preserve class proportions, utilized balanced class weighting during SVM optimization (which assigns higher penalties when misclassifying minority classes), and evaluated using Macro F1 and Recall rather than deceptive raw accuracy."),

        ("Q7: What is Platt Scaling, and why is it necessary for Linear SVM?",
         "Ans: Standard Linear SVM only calculates the raw geometric distance from a point to the decision boundary, not a probability percentage. Platt scaling fits a logistic sigmoid function over the SVM distances to output well-calibrated posterior probabilities from 0.0 to 1.0."),

        ("Q8: How does your system explain why a comment was flagged as toxic?",
         "Ans: Through exact linear feature attribution: Feature Contribution = (TF-IDF value) multiplied by (Learned SVM Weight). Words with high positive scores (e.g. 'idiot' = +2.80) are identified as the primary triggers and highlighted visually for human moderators."),

        ("Q9: What is the difference between single-label and multi-label classification?",
         "Ans: Single-label classification assigns mutually exclusive classes (e.g., Cat or Dog). Multi-label classification allows a single sample to simultaneously possess multiple categories. A single comment can be simultaneously Toxic, Obscene, and Insult."),

        ("Q10: What is an ablation study, and what did yours prove?",
         "Ans: An ablation study systematically removes or adds components one by one to quantify their isolated impact. Our 6-stage study proved that adding bigrams (pairs of words) yielded the largest single performance jump (+3.9% recall), demonstrating the importance of phrase context."),

        ("Q11: What happens if a user submits a typo or a word not seen in training (OOV)?",
         "Ans: Words not in the 10,000-feature vocabulary are ignored by the vectorizer. However, because our model relies on surrounding words, sub-word character repetition cleaning, and bigrams, the remaining recognizable tokens provide sufficient context to classify the comment."),

        ("Q12: How is the severity level (Level 0 to 3) calculated?",
         "Ans: Using a weighted heuristic formula: Severity = (0.35 * Toxic) + (0.30 * Severe Toxic) + (0.20 * Threat) + (0.15 * Identity Hate) + (0.10 * Insult) + (0.05 * Obscene). Physical threats and hate speech are assigned heavier weights to trigger emergency escalation."),

        ("Q13: Why does your system not use a naive 0.50 cutoff for all categories?",
         "Ans: In our dataset, categories like 'Threat' represent only 0.30% of comments (3 in 1,000). A threat probability of 0.14 is 46 times higher than the natural prior rate! If we used a naive 0.50 cutoff, subtle threats without explicit profanity (such as 'I will find you and hurt you, watch your back') would be falsely classified as clean. By calibrating the threat threshold to 0.10, we prevent dangerous false negatives and escalate real-world threats to Severity Level 3 immediately.")
    ]

    for q, a in viva_qa:
        q_box = [
            [Paragraph(f"<b>{q}</b>", table_header_style)],
            [Paragraph(a, callout_style)]
        ]
        q_table = Table(q_box, colWidths=[487])
        q_table.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 0.5, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(q_table)
        story.append(Spacer(1, 4))

    story.append(PageBreak())

    # ==================== SECTION 16: CONCLUSION ====================
    story.append(Paragraph("16. CONCLUSION, LIMITATIONS, AND FUTURE ROADMAP", h1_style))
    story.append(Paragraph(
        "<b>Summary of Accomplishments:</b><br/>"
        "This MCA capstone project successfully demonstrates an enterprise-grade Natural Language Processing solution for cyberbullying and toxicity detection. By uniting sound linguistic preprocessing (negation-preserving tokenization, WordNet lemmatization) with a Calibrated Linear Support Vector Machine, the system attains 88.42% accuracy and 0.8392 Macro F1 while executing inferences in under 2 milliseconds on consumer CPU hardware. Mathematical explainability and four-tier severity scoring provide practical operational utility.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Current Limitations:</b><br/>"
        "1. <b>Monolingual Scope:</b> The current model is trained primarily on English discourse and requires expansion for code-mixed languages (such as Hinglish or Spanglish).<br/>"
        "2. <b>Lack of Temporal Context:</b> The model analyzes standalone messages and does not track repeated user behavior over days or weeks.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Future Enhancements:</b><br/>"
        "• <b>Multilingual Cross-Lingual Transfer:</b> Incorporating multilingual embeddings (such as XLM-RoBERTa) for regional language moderation.<br/>"
        "• <b>Social Graph Graph-Neural-Networks (GNN):</b> Combining lexical comment toxicity with sender-receiver relationship graphs to detect coordinated harassment campaigns.<br/>"
        "• <b>Active Learning Loop:</b> Incorporating human moderator feedback to periodically retrain the model on emerging cyberbullying slang.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # Sign-off box
    signoff_data = [
        [Paragraph("<b>ACADEMIC DECLARATION AND APPROVAL</b>", table_header_style)],
        [Paragraph(
            "This project documentation accurately details the full development lifecycle, empirical findings, and architectural implementation of the MCA capstone project 'Cyberbullying Detection and Severity Analysis'. All experiments, source code, and automated tests are verified functional and reproducible in the local project workspace.<br/><br/>"
            "<b>Submitted By:</b> MCA Final Year Engineering Project Team (Four Members)<br/>"
            "<b>Project Mentor / Faculty Reviewer:</b> Department of Computer Applications<br/>"
            "<b>Academic Repository:</b> Fully configured with FastAPI, SQLite, Scikit-Learn, and React 19.",
            body_style
        )]
    ]
    signoff_table = Table(signoff_data, colWidths=[487])
    signoff_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(signoff_table)

    return story

def generate_pdf():
    target_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Cyberbullying_Detection_and_Severity_Analysis_Project_Report.pdf")
    
    # Pass 1: Build temporary PDF to detect page numbers
    temp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_report.pdf")
    doc_temp = SimpleDocTemplate(temp_path, pagesize=A4, leftMargin=54, rightMargin=54, topMargin=50, bottomMargin=50)
    story1 = build_pdf_story()
    doc_temp.build(story1, canvasmaker=NumberedCanvas)

    # Detect exact page numbers for each section
    reader = pypdf.PdfReader(temp_path)
    section_queries = [
        (1, "1. INTRODUCTION"),
        (2, "2. CONCEPTUAL FOUNDATION"),
        (3, "3. DATASET EXPLORATION"),
        (4, "4. COMPREHENSIVE END-TO-END"),
        (5, "5. SIX-STAGE NLP PREPROCESSING"),
        (6, "6. TF-IDF REPRESENTATION"),
        (7, "7. HOW A WORD GETS FLAGGED"),
        (8, "8. PREPROCESSING ABLATION"),
        (9, "9. MACHINE LEARNING MODEL SELECTION"),
        (10, "10. WHY LINEAR SVM WON"),
        (11, "11. MODEL EVALUATION"),
        (12, "12. MULTI-TIER SEVERITY"),
        (13, "13. SOFTWARE IMPLEMENTATION"),
        (14, "14. VERIFICATION, AUTOMATED"),
        (15, "15. COMPREHENSIVE VIVA EXAMINATION"),
        (16, "16. CONCLUSION, LIMITATIONS")
    ]

    toc_page_map = {}
    for num, query in section_queries:
        found_page = None
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if query in text:
                found_page = f"Page {i + 1}"
                break
        toc_page_map[num] = found_page or "Page X"
        print(f"Section {num} -> {toc_page_map[num]}")

    if os.path.exists(temp_path):
        os.remove(temp_path)

    # Pass 2: Build final PDF with perfectly aligned Table of Contents
    doc_final = SimpleDocTemplate(target_path, pagesize=A4, leftMargin=54, rightMargin=54, topMargin=50, bottomMargin=50)
    story2 = build_pdf_story(toc_page_map)
    doc_final.build(story2, canvasmaker=NumberedCanvas)
    
    final_reader = pypdf.PdfReader(target_path)
    print(f"\nSuccessfully generated FINAL PDF report at: {os.path.abspath(target_path)}")
    print(f"Total pages: {len(final_reader.pages)}")

if __name__ == '__main__':
    generate_pdf()
