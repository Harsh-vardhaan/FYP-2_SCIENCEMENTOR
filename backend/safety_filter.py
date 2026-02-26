"""Safety filter for non-Science content."""
import re
from typing import Tuple

# Keywords that indicate Science-related questions
# ==== BIOLOGY KEYWORDS ====
BIOLOGY_KEYWORDS = [
    # Cell biology
    "cell", "nucleus", "mitochondria", "ribosome", "membrane", "organelle",
    "chloroplast", "vacuole", "cytoplasm", "endoplasmic", "golgi",
    # Cell division
    "mitosis", "meiosis", "chromosome", "prophase", "metaphase",
    "anaphase", "telophase", "diploid", "haploid", "cell cycle",
    # Enzymes
    "enzyme", "substrate", "active site", "catalyst", "amylase", "protease",
    "lipase", "denature", "lock and key", "metabolism",
    # Photosynthesis
    "photosynthesis", "chlorophyll", "glucose", "calvin", "thylakoid", "stroma",
    # Respiration
    "respiration", "aerobic", "anaerobic", "atp", "glycolysis", "fermentation",
    "lactic acid", "ethanol", "krebs", "electron transport",
    # Diffusion and osmosis
    "diffusion", "osmosis", "concentration", "hypotonic", "hypertonic",
    "isotonic", "turgid", "plasmolysis", "permeable", "active transport",
    # Digestive system
    "digestion", "stomach", "intestine", "liver", "pancreas", "bile",
    "absorption", "villi", "saliva", "pepsin", "nutrition",
    # Circulatory system
    "heart", "blood", "artery", "vein", "capillary", "circulation",
    "hemoglobin", "platelet", "plasma", "pulse", "lymph",
    # Respiratory system
    "lung", "alveoli", "gas exchange", "breathing", "diaphragm",
    # Nervous system
    "neuron", "nerve", "synapse", "reflex", "brain", "spinal cord",
    "sensory", "motor", "impulse", "neurotransmitter", "receptor",
    # Endocrine system
    "hormone", "insulin", "glucagon", "adrenaline", "thyroid",
    "pituitary", "endocrine", "homeostasis", "feedback",
    # Reproduction
    "reproduction", "sperm", "egg", "ovary", "testes", "fertilization",
    "embryo", "fetus", "menstrual", "pregnancy", "puberty", "gamete",
    # Excretion
    "kidney", "nephron", "urine", "excretion", "osmoregulation",
    # DNA and genes
    "dna", "gene", "protein", "replication", "transcription",
    "translation", "mutation", "hereditary", "nucleotide", "base pair",
    "allele", "genotype", "phenotype", "dominant", "recessive", "punnett",
    # Ecology
    "ecosystem", "ecology", "food chain", "food web", "producer", "consumer",
    "decomposer", "carbon cycle", "nitrogen cycle", "biodiversity",
    "population", "community", "habitat", "niche", "trophic",
    # Evolution
    "evolution", "natural selection", "adaptation", "species", "speciation",
    "fossil", "darwin", "fitness", "variation",
    # Biotechnology
    "biotechnology", "genetic engineering", "pcr", "cloning", "crispr",
    "gel electrophoresis", "plasmid", "vector", "transgenic", "gmo",
    # General biology
    "biology", "biologi", "living", "organism", "life", "plant", "animal",
    "human body", "tissue", "organ", "system",
    # Malay terms
    "sel", "nukleus", "enzim", "fotosintesis", "respirasi",
    "pencernaan", "jantung", "darah", "saraf", "hormon", "pembiakan",
    "ekologi", "evolusi"
]

# ==== PHYSICS KEYWORDS ====
PHYSICS_KEYWORDS = [
    # Mechanics
    "physics", "force", "velocity", "acceleration", "gravity", "newton",
    "momentum", "friction", "mass", "weight", "inertia", "motion",
    "kinetic energy", "potential energy", "work", "power", "joule",
    "displacement", "speed", "vector", "scalar", "projectile",
    # Waves
    "wave", "frequency", "wavelength", "amplitude", "oscillation",
    "sound", "ultrasound", "echo", "reflection", "refraction", "diffraction",
    "interference", "longitudinal", "transverse", "hertz",
    # Electricity and Magnetism
    "electricity", "magnet", "circuit", "voltage", "current", "resistance",
    "ohm", "ampere", "volt", "capacitor", "inductor", "transformer",
    "electromagnetic", "field", "charge", "coulomb", "conductor", "insulator",
    "semiconductor", "diode", "transistor",
    # Thermodynamics
    "temperature", "heat", "thermal", "conduction", "convection", "radiation",
    "specific heat", "latent heat", "entropy", "thermodynamics", "kelvin",
    "celsius", "fahrenheit", "expansion",
    # Light and Optics
    "light", "optics", "lens", "mirror", "prism", "spectrum", "photon",
    "absorption", "emission", "laser", "optical",
    # Modern Physics
    "quantum", "relativity", "einstein", "nuclear", "radioactive", "decay",
    "half-life", "fission", "fusion", "isotope",
    # Malay terms
    "fizik", "daya", "halaju", "pecutan", "graviti", "momentum",
    "gelombang", "elektrik", "magnet", "litar", "voltan", "arus", "rintangan",
    "haba", "cahaya", "optik", "tenaga"
]

# ==== CHEMISTRY KEYWORDS ====
CHEMISTRY_KEYWORDS = [
    # Atomic Structure
    "chemistry", "atom", "molecule", "element", "compound", "electron", "proton",
    "neutron", "ion", "isotope", "atomic number", "mass number", "orbital",
    "shell", "valence", "periodic table", "group", "period",
    # Chemical Bonding
    "bond", "covalent", "ionic", "metallic", "hydrogen bond", "van der waals",
    "electronegativity", "polarity", "dipole",
    # Reactions
    "reaction", "reactant", "product", "catalyst", "equilibrium",
    "exothermic", "endothermic", "combustion", "neutralization",
    "oxidation", "reduction", "redox", "precipitate",
    # Acids and Bases
    "acid", "base", "alkali", "ph", "indicator", "titration", "buffer",
    "hydrochloric", "sulfuric", "nitric", "sodium hydroxide",
    # States of Matter
    "solid", "liquid", "gas", "sublimation", "evaporation", "condensation",
    "melting", "boiling", "freezing", "state of matter",
    # Solutions
    "solution", "solute", "solvent", "concentration", "molarity", "dilution",
    "saturated", "supersaturated", "solubility",
    # Organic Chemistry
    "organic", "carbon", "hydrocarbon", "alkane", "alkene", "alkyne",
    "alcohol", "carboxylic", "ester", "amine", "polymer", "monomer",
    "isomer", "functional group", "methane", "ethanol",
    # Electrochemistry
    "electrolysis", "electrode", "anode", "cathode", "electrolyte",
    "electrochemical", "galvanic", "battery", "cell",
    # Stoichiometry
    "mole", "avogadro", "stoichiometry", "empirical formula", "molecular formula",
    "limiting reagent", "yield", "percentage composition",
    # Malay terms
    "kimia", "atom", "molekul", "unsur", "sebatian", "tindak balas",
    "asid", "bes", "garam", "larutan", "elektrolisis", "ikatan"
]

# All science keywords combined
SCIENCE_KEYWORDS = BIOLOGY_KEYWORDS + PHYSICS_KEYWORDS + CHEMISTRY_KEYWORDS

# Topics that are explicitly outside scope
OFF_TOPIC_KEYWORDS = [
    # Math (unless applied to science)
    "math", "mathematics", "algebra", "geometry", "calculus",
    "probability", "statistics",
    # Inappropriate
    "hack", "cheat", "answer key", "exam answers"
]


def is_science_question(question: str) -> Tuple[bool, str]:
    """Check if a question is related to Science (Biology, Physics, or Chemistry).
    
    Args:
        question: The user's question.
        
    Returns:
        Tuple of (is_science, message).
        If not Science, message contains a polite redirect.
    """
    question_lower = question.lower()

    # Check for off-topic keywords first
    for keyword in OFF_TOPIC_KEYWORDS:
        if keyword in question_lower:
            if keyword in ["math", "mathematics", "algebra", "geometry", "calculus"]:
                return (
                    False,
                    f"I notice you're asking about {keyword.title()}. "
                    f"I'm SCIENCEMENTOR, your Science tutor! 🔬 "
                    f"I can help with Biology, Physics, and Chemistry topics. "
                    f"Do you have any Science questions?"
                )
            elif keyword in ["hack", "cheat", "answer key", "exam answers"]:
                return (
                    False,
                    "I'm here to help you learn and understand Science, "
                    "not to provide exam answers. Let me explain concepts "
                    "so you can answer questions on your own! "
                    "What Science topic would you like to learn about?"
                )

    # Check for science keywords
    for keyword in SCIENCE_KEYWORDS:
        if keyword in question_lower:
            return (True, "")

    # If no specific keywords found, give benefit of the doubt
    # but remind about scope
    if len(question.split()) < 3:
        return (
            False,
            "Could you please ask a more specific Science question? "
            "I can help with topics like:\n"
            "🧬 **Biology**: Cells, DNA, human body systems, ecology\n"
            "⚡ **Physics**: Forces, waves, electricity, energy\n"
            "🧪 **Chemistry**: Atoms, reactions, acids & bases, organic chemistry"
        )

    # Default: If no science keywords matched, REJECT it.
    # Strict mode as requested.
    return (
        False,
        "I'm sorry, but I can only answer questions about Physics, Biology, and Chemistry. "
        "Please ask a Science-related question! 🔬"
    )


# Keep backward compatibility alias
def is_biology_question(question: str) -> Tuple[bool, str]:
    """Alias for is_science_question for backward compatibility."""
    return is_science_question(question)


def validate_subject_scope(question: str, subject: str, is_guided: bool = False) -> Tuple[bool, str]:
    """Check if a question is valid for the selected subject.
    
    Args:
        question: The user's question.
        subject: The selected subject (Biology, Physics, Chemistry).
        is_guided: Whether the user is in guided mode (answering a question).
        
    Returns:
        Tuple of (is_valid, message).
    """
    if not subject:
        # If no subject selected (legacy sessions), fall back to general check
        # But if guided, we should be lenient too?
        if is_guided:
             # Check for off-topic keywords only
            for keyword in OFF_TOPIC_KEYWORDS:
                if keyword in question.lower():
                     if keyword in ["math", "mathematics", "algebra", "geometry", "calculus"]:
                        return (False, f"I notice you're asking about {keyword.title()}. Please stay on Science topics!")
                     return (False, "Please keep the conversation focused on learning Science.")
            return (True, "")
            
        return is_science_question(question)
        
    subject = subject.title()
    question_lower = question.lower()
    
    # Check for off-topic keywords ALWAYS (safety first)
    for keyword in OFF_TOPIC_KEYWORDS:
        if keyword in question_lower:
             return (
                False,
                f"I notice you're asking about {keyword.title()}. "
                f"You are currently in **{subject} Mode**. "
                f"Please ask a {subject} question or switch subjects!"
            )

    # If in guided mode, we assume the user is answering a question or following a guide.
    # We SKIP strict subject keyword checks and length checks.
    if is_guided:
        return (True, "")
    
    # map subject to keywords
    subject_keywords = []
    if subject == "Biology":
        subject_keywords = BIOLOGY_KEYWORDS
    elif subject == "Physics":
        subject_keywords = PHYSICS_KEYWORDS
    elif subject == "Chemistry":
        subject_keywords = CHEMISTRY_KEYWORDS
    else:
        # Fallback for unknown subjects
        return is_science_question(question)
        
    # Check for direct keyword match
    for keyword in subject_keywords:
        if keyword in question_lower:
            return (True, "")
            
    # Soft check for short queries
    if len(question.split()) < 3:
         return (
            False,
            f"Could you please ask a more specific **{subject}** question? "
            f"I am currently focused on {subject} topics."
        )
        
    # Check if it belongs to ANOTHER subject
    other_subjects = {
        "Biology": BIOLOGY_KEYWORDS,
        "Physics": PHYSICS_KEYWORDS,
        "Chemistry": CHEMISTRY_KEYWORDS
    }
    
    for other_subj, keywords in other_subjects.items():
        if other_subj == subject:
            continue
        for kw in keywords:
            if kw in question_lower:
                return (
                    False,
                    f"That sounds like a **{other_subj}** question! "
                    f"You are currently in **{subject} Mode**. "
                    f"Please change the subject to {other_subj} to ask this question."
                )

    # If no specific keywords found, we must be strict
    # The user requested ONLY Science questions.
    return (
        False,
        f"I notice you're asking a question that doesn't seem to be about {subject}. "
        f"I'm SCIENCEMENTOR, and I'm strictly focused on Science topics! 🔬 "
        f"Please ask me about Biology, Physics, or Chemistry."
    )


def get_relevant_context(question: str, knowledge_base: dict) -> str:
    """Get relevant context from the knowledge base.
    
    Args:
        question: The user's question.
        knowledge_base: The loaded knowledge base dictionary.
        
    Returns:
        Relevant context string or empty string if none found.
    """
    question_lower = question.lower()
    relevant_parts = []

    topics = knowledge_base.get("topics", {})
    
    # Biology topic keywords
    topic_keywords = {
        # Biology
        "cell_structure": ["cell", "nucleus", "mitochondria", "organelle", "membrane", "chloroplast", "vacuole"],
        "cell_division": ["mitosis", "meiosis", "division", "chromosome", "diploid", "haploid", "cell cycle"],
        "enzymes": ["enzyme", "substrate", "catalyst", "amylase", "protease", "lipase", "denature", "metabolism"],
        "photosynthesis": ["photosynthesis", "chlorophyll", "light", "glucose", "carbon dioxide"],
        "respiration": ["respiration", "aerobic", "anaerobic", "atp", "energy", "krebs"],
        "diffusion_osmosis": ["diffusion", "osmosis", "concentration", "hypotonic", "hypertonic", "water movement", "transport"],
        "digestive_system": ["digestion", "stomach", "intestine", "enzyme", "absorption", "food", "nutrition"],
        "circulatory_system": ["heart", "blood", "artery", "vein", "circulation", "hemoglobin"],
        "dna_genes": ["dna", "gene", "chromosome", "protein", "replication", "mutation", "allele", "genotype"],
        "nervous_system": ["neuron", "nerve", "brain", "synapse", "reflex", "impulse", "receptor"],
        "endocrine_system": ["hormone", "insulin", "glucagon", "adrenaline", "endocrine", "homeostasis"],
        "reproduction": ["reproduction", "sperm", "egg", "fertilization", "embryo", "menstrual", "pregnancy"],
        "ecology": ["ecosystem", "ecology", "food chain", "food web", "carbon cycle", "biodiversity"],
        "evolution": ["evolution", "natural selection", "adaptation", "species", "darwin", "fossil"],
        "biotechnology": ["biotechnology", "genetic engineering", "pcr", "cloning", "crispr", "gel electrophoresis"],
        # Physics
        "mechanics": ["force", "velocity", "acceleration", "momentum", "newton", "motion", "inertia", "gravity"],
        "waves": ["wave", "frequency", "wavelength", "sound", "oscillation", "reflection", "refraction"],
        "electricity": ["electricity", "circuit", "voltage", "current", "resistance", "ohm", "capacitor"],
        "thermodynamics": ["heat", "temperature", "thermal", "conduction", "convection", "entropy"],
        "optics": ["light", "lens", "mirror", "prism", "spectrum", "reflection", "refraction"],
        # Chemistry
        "atomic_structure": ["atom", "electron", "proton", "neutron", "orbital", "shell", "periodic table"],
        "chemical_bonding": ["bond", "covalent", "ionic", "electronegativity", "polarity"],
        "chemical_reactions": ["reaction", "catalyst", "equilibrium", "exothermic", "endothermic", "oxidation"],
        "acids_bases": ["acid", "base", "ph", "titration", "neutralization", "indicator"],
        "organic_chemistry": ["organic", "hydrocarbon", "alkane", "alkene", "alcohol", "polymer", "isomer"]
    }

    for topic_key, keywords in topic_keywords.items():
        if any(kw in question_lower for kw in keywords):
            topic_data = topics.get(topic_key, {})
            if topic_data:
                # Add topic name
                relevant_parts.append(f"Topic: {topic_data.get('name', topic_key)}")
                
                # Add relevant concepts
                concepts = topic_data.get("concepts", [])
                for concept in concepts[:3]:  # Limit to 3 concepts
                    if isinstance(concept, dict):
                        term = concept.get("term", "")
                        definition = concept.get("definition", "")
                        if term and definition:
                            relevant_parts.append(f"- {term}: {definition}")

    return "\n".join(relevant_parts) if relevant_parts else ""
