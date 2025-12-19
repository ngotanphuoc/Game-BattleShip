"""
Database Migration Script
Adds statistics columns to users table
"""
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.db_config import get_db_connection
import mysql.connector

def run_migration():
    """Run database migration to add user statistics columns"""
    
    print("🔄 Starting database migration...")
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Check if columns already exist
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'battleship' 
            AND TABLE_NAME = 'users' 
            AND COLUMN_NAME = 'wins'
        """)
        
        exists = cursor.fetchone()[0] > 0
        
        if exists:
            print("⚠️  Columns already exist. Skipping migration.")
            return
        
        print("📝 Adding columns: wins, losses, draws, total_games")
        
        # Add columns
        cursor.execute("""
            ALTER TABLE `users` 
            ADD COLUMN `wins` INT DEFAULT 0 AFTER `password`,
            ADD COLUMN `losses` INT DEFAULT 0 AFTER `wins`,
            ADD COLUMN `draws` INT DEFAULT 0 AFTER `losses`,
            ADD COLUMN `total_games` INT DEFAULT 0 AFTER `draws`
        """)
        
        connection.commit()
        print("✅ Columns added successfully")
        
        # Update existing users stats
        print("📊 Calculating stats for existing users...")
        
        cursor.execute("""
            UPDATE users u
            SET 
                wins = (
                    SELECT COUNT(*) 
                    FROM game_history 
                    WHERE user_id = u.id AND result = 'win'
                ),
                losses = (
                    SELECT COUNT(*) 
                    FROM game_history 
                    WHERE user_id = u.id AND result = 'lose'
                ),
                total_games = (
                    SELECT COUNT(*) 
                    FROM game_history 
                    WHERE user_id = u.id
                )
        """)
        
        connection.commit()
        print("✅ Stats calculated successfully")
        
        # Show results
        cursor.execute("SELECT id, username, wins, losses, draws, total_games FROM users")
        users = cursor.fetchall()
        
        print("\n📋 User Statistics:")
        print("-" * 70)
        print(f"{'ID':<5} {'Username':<15} {'Wins':<8} {'Losses':<8} {'Draws':<8} {'Total':<8}")
        print("-" * 70)
        for user in users:
            print(f"{user[0]:<5} {user[1]:<15} {user[2]:<8} {user[3]:<8} {user[4]:<8} {user[5]:<8}")
        print("-" * 70)
        
        cursor.close()
        connection.close()
        
        print("\n✅ Migration completed successfully!")
        print("🚀 You can now restart the server and login.")
        
    except mysql.connector.Error as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
