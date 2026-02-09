"""
PII Masking Utility Module
Detects and masks sensitive personally identifiable information before sending to APIs
"""

import re
from typing import Dict, Tuple


class PIIMasker:
    """Handles detection and masking of PII in text"""
    
    def __init__(self):
        self.pii_patterns = {
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'account_number': r'\b(?:account|acct)[\s#:]*(\d{6,18})\b',
            'routing_number': r'\b(?:routing|aba)[\s#:]*(\d{9})\b',
            # Address pattern (simple version)
            'address': r'\b\d+\s+[A-Za-z0-9\s,]+(?:street|st|avenue|ave|road|rd|boulevard|blvd|lane|ln|drive|dr|court|ct|way)\b'
        }
        
        self.pii_counters = {}
        self.masked_mapping = {}
    
    def mask_text(self, text: str) -> Tuple[str, Dict]:
        """
        Mask PII in text and return masked text with metadata
        
        Args:
            text: Original text potentially containing PII
            
        Returns:
            Tuple of (masked_text, metadata_dict)
        """
        masked_text = text
        metadata = {
            'original_length': len(text),
            'pii_detected': [],
            'mask_count': 0
        }
        
        # Reset counters for this text
        self.pii_counters = {}
        
        # Process each PII type
        for pii_type, pattern in self.pii_patterns.items():
            matches = list(re.finditer(pattern, masked_text, re.IGNORECASE))
            
            if matches:
                metadata['pii_detected'].append(pii_type)
                
                # Replace matches with placeholders
                for match in reversed(matches):  # Reverse to maintain indices
                    count = self.pii_counters.get(pii_type, 0) + 1
                    self.pii_counters[pii_type] = count
                    
                    placeholder = f"<{pii_type.upper()}_{count}>"
                    original_value = match.group(0)
                    
                    # Store mapping for potential unmasking
                    self.masked_mapping[placeholder] = original_value
                    
                    masked_text = masked_text[:match.start()] + placeholder + masked_text[match.end():]
                    metadata['mask_count'] += 1
        
        metadata['masked_length'] = len(masked_text)
        return masked_text, metadata
    
    def unmask_text(self, masked_text: str) -> str:
        """
        Unmask text by replacing placeholders with original values
        
        Args:
            masked_text: Text with PII placeholders
            
        Returns:
            Original text with PII restored
        """
        unmasked_text = masked_text
        
        for placeholder, original_value in self.masked_mapping.items():
            unmasked_text = unmasked_text.replace(placeholder, original_value)
        
        return unmasked_text
    
    def clear_mapping(self):
        """Clear stored PII mappings for security"""
        self.masked_mapping.clear()
        self.pii_counters.clear()


def mask_sensitive_data(text: str) -> Tuple[str, Dict]:
    """
    Convenience function to mask PII in text
    
    Args:
        text: Original text
        
    Returns:
        Tuple of (masked_text, metadata)
    """
    masker = PIIMasker()
    return masker.mask_text(text)


# Test the masker
if __name__ == "__main__":
    masker = PIIMasker()
    
    test_cases = [
        "My SSN is 123-45-6789 and my phone is (555) 123-4567",
        "Contact me at john.doe@example.com or call 555-123-4567",
        "My credit card is 4532-1234-5678-9010",
        "Account number 123456789 routing 021000021",
        "I live at 123 Main Street and make $5000 monthly"
    ]
    
    print("=== PII Masking Tests ===\n")
    for test in test_cases:
        masked, metadata = masker.mask_text(test)
        print(f"Original: {test}")
        print(f"Masked:   {masked}")
        print(f"Metadata: {metadata}")
        print()
