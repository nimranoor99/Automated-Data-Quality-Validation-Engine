import pandas as pd
import json
from datetime import datetime

class DataQualityEngine:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.read_excel(file_path)
        self.results = {}
        
    def run_all_checks(self):
        """Execute all quality checks"""
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'total_records': len(self.df),
            'checks': {}
        }
        
        # 1. DUPLICATE CHECK (Node_ID)
        duplicates = self.df[self.df.duplicated(['Node_ID'], keep=False)]
        self.results['checks']['duplicates'] = {
            'count': len(duplicates),
            'records': duplicates['Node_ID'].tolist() if len(duplicates) > 0 else []
        }
        
        # 2. MISSING FIELDS CHECK
        missing = self.df.isnull().sum()
        missing_fields = {
            'Node_Name': int(missing['Node_Name']),
            'IP_Address': int(missing['IP_Address']),
            'Status': int(missing['Status']),
            'Location': int(missing['Location'])
        }
        self.results['checks']['missing_fields'] = missing_fields
        
        # 3. CONFIGURATION DRIFT (IP format validation)
        invalid_ips = self.df[~self.df['IP_Address'].str.match(
            r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', na=False)]
        self.results['checks']['config_drift'] = {
            'invalid_ips_count': len(invalid_ips),
            'invalid_records': invalid_ips[['Node_ID', 'IP_Address']].to_dict('records')
        }
        
        # 4. STATUS HEALTH CHECK
        inactive = self.df[self.df['Status'] == 'Inactive']
        self.results['checks']['inactive_nodes'] = {
            'count': len(inactive),
            'nodes': inactive['Node_ID'].tolist()
        }
        
        # Calculate score (0-100)
        total_issues = (self.results['checks']['duplicates']['count'] + 
                       sum(self.results['checks']['missing_fields'].values()) + 
                       self.results['checks']['config_drift']['invalid_ips_count'])
        max_possible = len(self.df) * 4  # 4 check types
        score = max(0, 100 - (total_issues / max_possible * 100))
        self.results['quality_score'] = round(score, 1)
        
        return self.results

    def generate_report(self):
        """Generate human-readable report"""
        results = self.run_all_checks()
        report = f"""
        ========================================
        DATA QUALITY REPORT
        ========================================
        Timestamp: {results['timestamp']}
        Total Records: {results['total_records']}
        Quality Score: {results['quality_score']}/100
        
        ISSUES FOUND:
        ---------------
        • Duplicate Nodes: {results['checks']['duplicates']['count']}
        • Missing Node Names: {results['checks']['missing_fields']['Node_Name']}
        • Missing IPs: {results['checks']['missing_fields']['IP_Address']}
        • Missing Status: {results['checks']['missing_fields']['Status']}
        • Missing Locations: {results['checks']['missing_fields']['Location']}
        • Invalid IPs: {results['checks']['config_drift']['invalid_ips_count']}
        • Inactive Nodes: {results['checks']['inactive_nodes']['count']}
        """
        return report

# Standalone execution
if __name__ == "__main__":
    engine = DataQualityEngine('sample_data.xlsx')
    results = engine.run_all_checks()
    print(engine.generate_report())
    
    # Save JSON for API
    with open('quality_results.json', 'w') as f:
        json.dump(results, f, indent=2)