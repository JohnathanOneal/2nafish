#!/usr/bin/env python3

import sqlite3
import argparse
from datetime import datetime
import os


class IdeaManager:
    def __init__(self, dbName='ideas.db'):
        homeDir = os.path.expanduser("~")
        dbPath = os.path.join(homeDir, dbName)
        self.conn = sqlite3.connect(dbPath)
        self.createTable()

    def createTable(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            priority INTEGER,
            importance INTEGER,
            size INTEGER,
            status TEXT,
            tags TEXT,
            created_at DATETIME,
            updated_at DATETIME
        )
        ''')
        self.conn.commit()

    def addIdea(self, title, description=None, priority=None, importance=None, size=None, status='open', tags=None):
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute('''
        INSERT INTO ideas (title, description, priority, importance, size, status, tags, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, priority, importance, size, status, tags, now, now))
        self.conn.commit()
        print("Idea added successfully!")

    def listIdeas(self, sortBy='id', filterStatus='open', filterTag=None):
        cursor = self.conn.cursor()
        query = "SELECT * FROM ideas"
        conditions = []
        if filterStatus:
            conditions.append(f"status = '{filterStatus}'")
        if filterTag:
            conditions.append(f"tags LIKE '%{filterTag}%'")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += f" ORDER BY {sortBy}"
        cursor.execute(query)
        ideas = cursor.fetchall()

        if not ideas:
            print("No ideas found.")
            return

        print(f"{'ID':<5}{'Title':<20}{'Priority':<10}{'Importance':<12}{'Size':<8}{'Status':<8}{'Tags':<20}")
        print("-" * 83)
        for idea in ideas:
            print(
                f"{idea[0] or '-':<5}{idea[1][:18] or '-':<20}{idea[3] or '-':<10}{idea[4] or '-':<12}{idea[5] or '-':<8}{idea[6] or '-':<8}{idea[7][:18]  or '-':<20}")

    def listTitlesAndDescriptions(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, description FROM ideas ORDER BY id")
        ideas = cursor.fetchall()

        if not ideas:
            print("No ideas found.")
            return

        for idea in ideas:
            print(f"ID: {idea[0]}")
            print(f"Title: {idea[1]}")
            print(f"Description: {idea[2] or 'No description'}")
            print("-" * 40)

    def updateIdea(self, id, newStatus=None, newTags=None):
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        updates = []
        params = []
        if newStatus:
            updates.append("status = ?")
            params.append(newStatus)
        if newTags:
            updates.append("tags = ?")
            params.append(newTags)
        updates.append("updated_at = ?")
        params.append(now)
        params.append(id)

        query = f"UPDATE ideas SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        self.conn.commit()
        print(f"Idea {id} updated successfully!")

    def close(self):
        self.conn.close()


def main():
    parser = argparse.ArgumentParser(description="2nafish - Idea Manager")
    parser.add_argument('action', choices=['add', 'list', 'update', 'list-details'], help='Action to perform')
    parser.add_argument('--title', help='Title of the idea')
    parser.add_argument('--description', help='Description of the idea')
    parser.add_argument('--priority', type=int, choices=range(1, 6), help='Priority (1-5)')
    parser.add_argument('--importance', type=int, choices=range(1, 6), help='Importance (1-5)')
    parser.add_argument('--size', type=int, choices=range(1, 6), help='Size (1-5)')
    parser.add_argument('--tags', help='Comma-separated tags')
    parser.add_argument('--sort', choices=['id', 'priority', 'importance', 'size'], default='id', help='Sort ideas by')
    parser.add_argument('--filter-status', choices=['open', 'closed', 'all'], default='open', help='Filter ideas by status (default: open)')
    parser.add_argument('--filter-tag', help='Filter ideas by tag')
    parser.add_argument('--id', type=int, help='ID of the idea to update')
    parser.add_argument('--new-status', choices=['open', 'closed'], help='New status for the idea')
    parser.add_argument('--new-tags', help='New tags for the idea')

    args = parser.parse_args()
    manager = IdeaManager()

    if args.action == 'add':
        if not args.title:
            print("Error: Title is required for adding an idea.")
            return
        manager.addIdea(args.title, args.description, args.priority, args.importance, args.size, tags=args.tags)
    elif args.action == 'list':
        filterStatus = None if args.filter_status == 'all' else args.filter_status
        manager.listIdeas(args.sort, filterStatus, args.filter_tag)
    elif args.action == 'update':
        if args.id and (args.new_status or args.new_tags):
            manager.updateIdea(args.id, args.new_status, args.new_tags)
        else:
            print("Error: ID and either new status or new tags are required for updating an idea.")
    elif args.action == 'list-details':
        manager.listTitlesAndDescriptions()

    manager.close()


if __name__ == "__main__":
    main()
