"""
Problems Data Cleaning Service

This service handles data quality issues in the problems collection:
- Missing values (category, description, etc.)
- Typos and inconsistencies
- Standardization of domain values
- Data validation and enrichment
"""

import re
import logging
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class ProblemsDataCleaningService:
    """Service for cleaning and standardizing problems data"""

    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URL)
        self.db = self.client.mental_health_db
        self.problems_collection = self.db.problems

        # Domain to category mapping
        self.domain_category_mapping = {
            'anxiety': 'Anxiety',
            'stress': 'Stress',
            'trauma': 'Trauma',
            'general': 'General'
        }

        # Common typos and corrections
        self.typo_corrections = {
            'Exan/ test anxiety': 'Exam/Test Anxiety',
            'Transition/ adjustment anxiety': 'Transition/Adjustment Anxiety',
            'Panic attacks (disorder)': 'Panic Disorder',
            'Generalized anxiety - Mild': 'Generalized Anxiety - Mild',
            'Generalized anxiety - Moderate': 'Generalized Anxiety - Moderate',
            'Generalized anxiety - Severe': 'Generalized Anxiety - Severe',
            'Separation Anxiety': 'Separation Anxiety Disorder',
            'Stress - panic atttack ?': 'Stress - Panic Attack',
            'P004 -2': 'P004-2',
            'P005-1 – Adjustment Disorder': 'P005-1 - Adjustment Disorder',
            'P005-2 – Acute Trauma': 'P005-2 - Acute Trauma',
            'P005-3 – PTSD (Post-Traumatic Stress Disorder)': 'P005-3 - PTSD (Post-Traumatic Stress Disorder)',
            'P005-4 – Complex Trauma': 'P005-4 - Complex Trauma',
            'P005-5 – Childhood Trauma': 'P005-5 - Childhood Trauma',
            'P005-6 – Medical Trauma': 'P005-6 - Medical Trauma',
            'P005-7 – Traumatic Grief / Loss': 'P005-7 - Traumatic Grief/Loss'
        }

        # Problem name patterns for category inference
        self.category_patterns = {
            'anxiety': [
                'anxiety', 'panic', 'worry', 'fear', 'phobia', 'social anxiety',
                'generalized anxiety', 'separation anxiety', 'exam anxiety', 'test anxiety'
            ],
            'stress': [
                'stress', 'workplace', 'work', 'pressure', 'burnout', 'overwhelm',
                'emotional dysregulation', 'acute stress', 'chronic stress'
            ],
            'trauma': [
                'trauma', 'ptsd', 'post-traumatic', 'acute trauma', 'complex trauma',
                'childhood trauma', 'medical trauma', 'traumatic grief', 'loss'
            ],
            'depression': [
                'depression', 'depressed', 'sadness', 'hopelessness', 'worthlessness'
            ]
        }

    def clean_all_problems(self) -> Dict[str, Any]:
        """Clean all problems in the database"""
        logger.info("Starting comprehensive problems data cleaning...")

        results = {
            'total_processed': 0,
            'updated': 0,
            'errors': 0,
            'fixes_applied': {
                'missing_categories': 0,
                'typos_fixed': 0,
                'domains_standardized': 0,
                'descriptions_improved': 0,
                'severity_levels_added': 0
            }
        }

        try:
            # Get all problems
            problems = list(self.problems_collection.find({}))
            results['total_processed'] = len(problems)

            for problem in problems:
                try:
                    cleaned_problem = self.clean_single_problem(problem)
                    if cleaned_problem != problem:
                        # Update the problem in database
                        self.problems_collection.update_one(
                            {'_id': problem['_id']},
                            {'$set': cleaned_problem}
                        )
                        results['updated'] += 1

                        # Count specific fixes
                        fixes = self._count_fixes(problem, cleaned_problem)
                        for fix_type, count in fixes.items():
                            results['fixes_applied'][fix_type] += count

                except Exception as e:
                    logger.error(f"Error cleaning problem {problem.get('_id')}: {str(e)}")
                    results['errors'] += 1

        except Exception as e:
            logger.error(f"Error in clean_all_problems: {str(e)}")
            results['errors'] += 1

        logger.info(f"Problems cleaning completed: {results}")
        return results

    def clean_single_problem(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Clean a single problem document"""
        cleaned = problem.copy()

        # 1. Fix missing categories
        if not cleaned.get('category') or cleaned.get('category') == 'None':
            cleaned['category'] = self._infer_category(cleaned)

        # 2. Fix typos in problem names
        if cleaned.get('problem_name'):
            cleaned['problem_name'] = self._fix_typos(cleaned['problem_name'])

        # 3. Standardize domain values
        if cleaned.get('domain'):
            cleaned['domain'] = self._standardize_domain(cleaned['domain'])

        # 4. Improve descriptions
        if cleaned.get('description'):
            cleaned['description'] = self._improve_description(cleaned['description'])
        elif not cleaned.get('description') and cleaned.get('problem_name'):
            # Generate description from problem name if missing
            cleaned['description'] = self._generate_description(cleaned['problem_name'])

        # 5. Add missing severity levels
        if not cleaned.get('severity_level'):
            cleaned['severity_level'] = self._infer_severity_level(cleaned)

        # 6. Ensure required fields
        if not cleaned.get('is_active'):
            cleaned['is_active'] = True

        # 7. Clean up None values
        cleaned = self._clean_none_values(cleaned)

        return cleaned

    def _infer_category(self, problem: Dict[str, Any]) -> str:
        """Infer category from domain, problem name, or description"""
        # First try domain mapping
        domain = problem.get('domain', '') or ''
        if domain and domain.lower() in self.domain_category_mapping:
            return self.domain_category_mapping[domain.lower()]

        # Try problem name patterns
        problem_name = problem.get('problem_name', '') or ''
        description = problem.get('description', '') or ''
        text_to_check = f"{problem_name} {description}".lower()

        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if pattern in text_to_check:
                    return category.title()

        # Default based on domain
        if domain:
            return domain.title()

        return 'General'

    def _fix_typos(self, text: str) -> str:
        """Fix common typos in problem names"""
        if not text or text == 'None':
            return text

        # Apply typo corrections
        for typo, correction in self.typo_corrections.items():
            if typo in text:
                text = text.replace(typo, correction)

        # Fix common patterns
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'–', '-', text)    # En dash to hyphen
        text = re.sub(r'/', '/', text)    # Normalize slashes
        text = text.strip()

        return text

    def _standardize_domain(self, domain: str) -> str:
        """Standardize domain values"""
        if not domain or domain == 'None':
            return 'general'

        domain = domain.lower().strip()

        # Map variations to standard values
        domain_mapping = {
            'anx': 'anxiety',
            'str': 'stress',
            'tra': 'trauma',
            'gen': 'general',
            'dep': 'depression'
        }

        return domain_mapping.get(domain, domain)

    def _improve_description(self, description: str) -> str:
        """Improve description quality"""
        if not description or description == 'None':
            return description

        # Clean up description
        description = description.strip()

        # Fix common issues
        description = re.sub(r'\s+', ' ', description)  # Multiple spaces
        description = re.sub(r'\.{2,}', '.', description)  # Multiple periods

        # Ensure proper capitalization
        if description and not description[0].isupper():
            description = description[0].upper() + description[1:]

        return description

    def _generate_description(self, problem_name: str) -> str:
        """Generate a description from problem name"""
        if not problem_name or problem_name == 'None':
            return ""

        # Simple description generation based on problem name
        name_lower = problem_name.lower()

        if 'anxiety' in name_lower:
            return f"Anxiety-related condition: {problem_name}"
        elif 'stress' in name_lower:
            return f"Stress-related condition: {problem_name}"
        elif 'trauma' in name_lower:
            return f"Trauma-related condition: {problem_name}"
        elif 'depression' in name_lower:
            return f"Depression-related condition: {problem_name}"
        else:
            return f"Mental health condition: {problem_name}"

    def _infer_severity_level(self, problem: Dict[str, Any]) -> int:
        """Infer severity level from problem characteristics"""
        problem_name = problem.get('problem_name', '') or ''
        description = problem.get('description', '') or ''
        text = f"{problem_name} {description}".lower()

        # High severity indicators
        if any(word in text for word in ['severe', 'severe', 'acute', 'crisis', 'emergency']):
            return 4

        # Medium-high severity
        if any(word in text for word in ['moderate', 'significant', 'chronic']):
            return 3

        # Medium severity
        if any(word in text for word in ['mild', 'minor', 'low']):
            return 2

        # Default to medium severity
        return 3

    def _clean_none_values(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Remove or fix None values"""
        cleaned = {}

        for key, value in problem.items():
            if value is None:
                # Set appropriate defaults for None values
                if key in ['category', 'description', 'problem_name']:
                    continue  # Skip None values for required fields
                elif key == 'is_active':
                    cleaned[key] = True
                elif key == 'severity_level':
                    cleaned[key] = 3
                else:
                    cleaned[key] = value
            else:
                cleaned[key] = value

        return cleaned

    def _count_fixes(self, original: Dict[str, Any], cleaned: Dict[str, Any]) -> Dict[str, int]:
        """Count the types of fixes applied"""
        fixes = {
            'missing_categories': 0,
            'typos_fixed': 0,
            'domains_standardized': 0,
            'descriptions_improved': 0,
            'severity_levels_added': 0
        }

        # Check for category fixes
        if (not original.get('category') or original.get('category') == 'None') and cleaned.get('category'):
            fixes['missing_categories'] = 1

        # Check for typo fixes
        if original.get('problem_name') != cleaned.get('problem_name'):
            fixes['typos_fixed'] = 1

        # Check for domain standardization
        if original.get('domain') != cleaned.get('domain'):
            fixes['domains_standardized'] = 1

        # Check for description improvements
        if original.get('description') != cleaned.get('description'):
            fixes['descriptions_improved'] = 1

        # Check for severity level additions
        if not original.get('severity_level') and cleaned.get('severity_level'):
            fixes['severity_levels_added'] = 1

        return fixes

    def validate_problem_data(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean problem data before insertion"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'cleaned_data': problem_data.copy()
        }

        # Required fields validation
        required_fields = ['problem_name', 'domain']
        for field in required_fields:
            if not problem_data.get(field):
                validation_result['errors'].append(f"Missing required field: {field}")
                validation_result['is_valid'] = False

        # Clean the data
        if validation_result['is_valid']:
            validation_result['cleaned_data'] = self.clean_single_problem(problem_data)

        return validation_result

    def get_data_quality_report(self) -> Dict[str, Any]:
        """Generate a data quality report for problems collection"""
        problems = list(self.problems_collection.find({}))

        report = {
            'total_problems': len(problems),
            'quality_issues': {
                'missing_categories': 0,
                'missing_descriptions': 0,
                'missing_severity_levels': 0,
                'inconsistent_domains': 0,
                'typos_detected': 0
            },
            'domain_distribution': {},
            'category_distribution': {}
        }

        domains = set()
        categories = set()

        for problem in problems:
            # Check for missing categories
            if not problem.get('category') or problem.get('category') == 'None':
                report['quality_issues']['missing_categories'] += 1

            # Check for missing descriptions
            if not problem.get('description'):
                report['quality_issues']['missing_descriptions'] += 1

            # Check for missing severity levels
            if not problem.get('severity_level'):
                report['quality_issues']['missing_severity_levels'] += 1

            # Collect domains and categories
            if problem.get('domain'):
                domains.add(problem['domain'])
            if problem.get('category'):
                categories.add(problem['category'])

        # Count distributions
        for domain in domains:
            count = self.problems_collection.count_documents({'domain': domain})
            report['domain_distribution'][domain] = count

        for category in categories:
            count = self.problems_collection.count_documents({'category': category})
            report['category_distribution'][category] = count

        return report

    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
