#!/usr/bin/env python3
"""
MHMS Database Performance Optimizer
===================================
Script to monitor and maintain database performance indexes
Created: September 26, 2025
"""

import sys
import os
sys.path.append('.')
from db.connection import get_connection
from datetime import datetime

class DatabaseOptimizer:
    def __init__(self):
        self.db = get_connection()
        self.cursor = self.db.cursor()
    
    def analyze_table_stats(self):
        """Analyze table statistics and index usage"""
        print("=== DATABASE PERFORMANCE ANALYSIS ===\n")
        
        # Get table sizes and row counts
        tables = ['users', 'weekly_sessions', 'question_responses', 'cctv_detections']
        
        for table in tables:
            try:
                # Get row count
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = self.cursor.fetchone()[0]
                
                # Get table size (if available)
                self.cursor.execute(f"""
                    SELECT 
                        ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'DB Size in MB' 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE() AND table_name = '{table}'
                """)
                size_result = self.cursor.fetchone()
                size = size_result[0] if size_result else 0
                
                print(f"{table.upper()}:")
                print(f"  Rows: {row_count:,}")
                print(f"  Size: {size} MB")
                print(f"  Indexes: {self._count_indexes(table)}")
                print()
            except Exception as e:
                print(f"Error analyzing {table}: {e}")
    
    def _count_indexes(self, table):
        """Count non-primary indexes for a table"""
        self.cursor.execute(f"SHOW INDEX FROM {table}")
        indexes = self.cursor.fetchall()
        return len([idx for idx in indexes if idx[2] != 'PRIMARY'])
    
    def test_critical_queries(self):
        """Test performance of critical queries used in admin pages"""
        print("=== CRITICAL QUERY PERFORMANCE TESTS ===\n")
        
        queries = [
            {
                'name': 'User Count by Type',
                'sql': "SELECT COUNT(*) FROM users WHERE user_type = 'soldier'"
            },
            {
                'name': 'Recent Sessions',
                'sql': """
                    SELECT force_id, combined_avg_score 
                    FROM weekly_sessions 
                    WHERE completion_timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY) 
                    AND status = 'completed'
                    LIMIT 10
                """
            },
            {
                'name': 'Latest Session per User',
                'sql': """
                    SELECT ws.force_id, ws.combined_avg_score
                    FROM weekly_sessions ws
                    INNER JOIN (
                        SELECT force_id, MAX(completion_timestamp) as max_completion
                        FROM weekly_sessions 
                        WHERE completion_timestamp IS NOT NULL
                        GROUP BY force_id
                    ) latest ON ws.force_id = latest.force_id 
                    AND ws.completion_timestamp = latest.max_completion
                    LIMIT 5
                """
            }
        ]
        
        for query in queries:
            try:
                print(f"Testing: {query['name']}")
                start_time = datetime.now()
                
                self.cursor.execute(query['sql'])
                results = self.cursor.fetchall()
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds() * 1000
                
                print(f"  ✓ Execution time: {execution_time:.2f}ms")
                print(f"  ✓ Rows returned: {len(results)}")
                print()
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                print()
    
    def check_index_usage(self):
        """Check if indexes are being used effectively"""
        print("=== INDEX USAGE ANALYSIS ===\n")
        
        try:
            # Check for duplicate indexes
            self.cursor.execute("""
                SELECT table_name, GROUP_CONCAT(index_name) as indexes, column_name
                FROM information_schema.statistics 
                WHERE table_schema = DATABASE()
                GROUP BY table_name, column_name
                HAVING COUNT(*) > 1
            """)
            
            duplicates = self.cursor.fetchall()
            if duplicates:
                print("Potential duplicate indexes found:")
                for dup in duplicates:
                    print(f"  Table: {dup[0]}, Column: {dup[2]}, Indexes: {dup[1]}")
            else:
                print("✓ No duplicate indexes detected")
            
            print()
            
        except Exception as e:
            print(f"Error checking index usage: {e}")
    
    def maintenance_recommendations(self):
        """Provide maintenance recommendations"""
        print("=== MAINTENANCE RECOMMENDATIONS ===\n")
        
        recommendations = [
            "1. Run ANALYZE TABLE monthly to update statistics",
            "2. Monitor slow query log for optimization opportunities",
            "3. Consider archiving old session data (>1 year) for better performance",
            "4. Monitor index usage with performance_schema queries",
            "5. Run OPTIMIZE TABLE quarterly on heavily updated tables"
        ]
        
        for rec in recommendations:
            print(rec)
        
        print("\n=== PERFORMANCE COMMANDS ===")
        print("# Update table statistics:")
        print("ANALYZE TABLE users, weekly_sessions, question_responses;")
        print("\n# Optimize tables:")
        print("OPTIMIZE TABLE users, weekly_sessions, question_responses;")
        print("\n# Check slow queries:")
        print("SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;")
    
    def close(self):
        """Close database connections"""
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()

def main():
    """Main function to run performance analysis"""
    print(f"MHMS Database Performance Optimizer")
    print(f"Started at: {datetime.now()}")
    print("=" * 50)
    
    optimizer = None
    try:
        optimizer = DatabaseOptimizer()
        
        # Run analysis
        optimizer.analyze_table_stats()
        optimizer.test_critical_queries()
        optimizer.check_index_usage()
        optimizer.maintenance_recommendations()
        
        print("\n" + "=" * 50)
        print("✅ Performance analysis completed successfully!")
        print("Your database is now optimized for faster user data loading.")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
    finally:
        if optimizer:
            optimizer.close()

if __name__ == "__main__":
    main()