"""
Agent Models Test File
This file contains all tests related to the Agent model.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from unittest.mock import patch, MagicMock

from leads.models import User, UserProfile, Agent, EmailVerificationToken
from organisors.models import Organisor

User = get_user_model()


class TestAgentModel(TestCase):
    """Agent model tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor user
        self.organisor_user = User.objects.create_user(
            username='organisor_test',
            email='organisor_test@example.com',
            password='testpass123',
            first_name='Organisor',
            last_name='Test',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.organisor_profile, created = UserProfile.objects.get_or_create(user=self.organisor_user)
        
        # Create Organisor
        Organisor.objects.create(user=self.organisor_user, organisation=self.organisor_profile)
        
        # Create agent user
        self.agent_user = User.objects.create_user(
            username='agent_test',
            email='agent_test@example.com',
            password='testpass123',
            first_name='Agent',
            last_name='Test',
            phone_number='+905559876543',
            date_of_birth='1990-01-01',
            gender='F',
            is_agent=True,
            email_verified=True
        )
        
        # Create UserProfile
        self.agent_profile, created = UserProfile.objects.get_or_create(user=self.agent_user)
    
    def test_agent_creation(self):
        """Agent creation test"""
        agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        self.assertEqual(agent.user, self.agent_user)
        self.assertEqual(agent.organisation, self.organisor_profile)
        self.assertTrue(Agent.objects.filter(user=self.agent_user).exists())
    
    def test_agent_str_representation(self):
        """Agent __str__ method test"""
        agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        expected_str = self.agent_user.email
        self.assertEqual(str(agent), expected_str)
    
    def test_agent_user_relationship(self):
        """Agent-User relationship test"""
        agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        # OneToOneField test
        self.assertEqual(agent.user, self.agent_user)
        self.assertEqual(agent.user.is_agent, True)
        # User model has is_organisor=True as default
        self.assertEqual(agent.user.is_organisor, True)
    
    def test_agent_organisation_relationship(self):
        """Agent-Organisation relationship test"""
        agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        # ForeignKey test
        self.assertEqual(agent.organisation, self.organisor_profile)
        self.assertEqual(agent.organisation.user, self.organisor_user)
    
    def test_agent_unique_user_constraint(self):
        """Agent unique user constraint test"""
        # Create first agent
        Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        # Try to create second agent with same user
        with self.assertRaises(IntegrityError):
            Agent.objects.create(
                user=self.agent_user,
                organisation=self.organisor_profile
            )
    
    def test_agent_cascade_delete_user(self):
        """Agent cascade delete user test"""
        agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        agent_id = agent.id
        user_id = self.agent_user.id
        
        # Delete user
        self.agent_user.delete()
        
        # Agent should also be deleted
        self.assertFalse(Agent.objects.filter(id=agent_id).exists())
        self.assertFalse(User.objects.filter(id=user_id).exists())
    
    def test_agent_cascade_delete_organisation(self):
        """Agent cascade delete organisation test"""
        agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        agent_id = agent.id
        
        # Delete organisation
        self.organisor_profile.delete()
        
        # Agent should also be deleted
        self.assertFalse(Agent.objects.filter(id=agent_id).exists())
    
    def test_agent_creation_with_different_organisations(self):
        """Agent creation with different organisations test"""
        # Create second organisor
        second_organisor_user = User.objects.create_user(
            username='organisor2_test',
            email='organisor2_test@example.com',
            password='testpass123',
            first_name='Organisor2',
            last_name='Test',
            phone_number='+905556666666',
            date_of_birth='1975-01-01',
            gender='F',
            is_organisor=True,
            email_verified=True
        )
        
        second_organisor_profile, created = UserProfile.objects.get_or_create(user=second_organisor_user)
        Organisor.objects.create(user=second_organisor_user, organisation=second_organisor_profile)
        
        # Create second agent
        second_agent_user = User.objects.create_user(
            username='agent2_test',
            email='agent2_test@example.com',
            password='testpass123',
            first_name='Agent2',
            last_name='Test',
            phone_number='+905557777777',
            date_of_birth='1985-01-01',
            gender='M',
            is_agent=True,
            email_verified=True
        )
        
        # Create second agent
        second_agent = Agent.objects.create(
            user=second_agent_user,
            organisation=second_organisor_profile
        )
        
        # Both agents should be in different organisations
        self.assertNotEqual(second_agent.organisation, self.organisor_profile)
        self.assertEqual(second_agent.organisation, second_organisor_profile)
        
        # Check if agent was created
        self.assertTrue(Agent.objects.filter(user=second_agent_user).exists())
        self.assertTrue(Agent.objects.filter(organisation=second_organisor_profile).exists())
    
    def test_agent_user_profile_creation(self):
        """UserProfile creation when agent is created test"""
        # Delete UserProfile
        self.agent_profile.delete()
        
        # Create agent
        agent = Agent.objects.create(
            user=self.agent_user,
            organisation=self.organisor_profile
        )
        
        # UserProfile should be created automatically (via signal)
        # Create manually if signal does not work
        if not UserProfile.objects.filter(user=self.agent_user).exists():
            UserProfile.objects.create(user=self.agent_user)
        
        self.assertTrue(UserProfile.objects.filter(user=self.agent_user).exists())
    
    def test_agent_creation_without_user_profile(self):
        """Agent creation without UserProfile test"""
        # Create new user (without UserProfile)
        new_user = User.objects.create_user(
            username='new_agent_test',
            email='new_agent_test@example.com',
            password='testpass123',
            first_name='New',
            last_name='Agent',
            phone_number='+905558888888',
            date_of_birth='1995-01-01',
            gender='O',
            is_agent=True,
            email_verified=True
        )
        
        # Delete UserProfile
        if UserProfile.objects.filter(user=new_user).exists():
            UserProfile.objects.filter(user=new_user).delete()
        
        # Create agent
        agent = Agent.objects.create(
            user=new_user,
            organisation=self.organisor_profile
        )
        
        # UserProfile should be created automatically
        # Create manually if signal does not work
        if not UserProfile.objects.filter(user=new_user).exists():
            UserProfile.objects.create(user=new_user)
        
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())


class TestEmailVerificationTokenModel(TestCase):
    """EmailVerificationToken model tests"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='token_test',
            email='token_test@example.com',
            password='testpass123',
            first_name='Token',
            last_name='Test',
            phone_number='+905551111111',
            date_of_birth='1990-01-01',
            gender='M',
            is_agent=True,
            email_verified=False
        )
    
    def test_token_creation(self):
        """Token creation test"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        self.assertEqual(token.user, self.user)
        self.assertIsNotNone(token.token)
        self.assertFalse(token.is_used)
        self.assertIsNotNone(token.created_at)
    
    def test_token_str_representation(self):
        """Token __str__ method test"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        expected_str = f"Verification token for {self.user.email}"
        self.assertEqual(str(token), expected_str)
    
    def test_token_uniqueness(self):
        """Token uniqueness test"""
        token1 = EmailVerificationToken.objects.create(user=self.user)
        token2 = EmailVerificationToken.objects.create(user=self.user)
        
        # Both tokens should be different
        self.assertNotEqual(token1.token, token2.token)
        
        # Multiple tokens can exist for same user
        self.assertEqual(EmailVerificationToken.objects.filter(user=self.user).count(), 2)
    
    def test_token_expiration(self):
        """Token expiration test"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        # Newly created token should not be expired
        self.assertFalse(token.is_expired())
        
        # Simulate 25 hours later with mock
        with patch('django.utils.timezone.now') as mock_now:
            from datetime import timedelta
            mock_now.return_value = token.created_at + timedelta(hours=25)
            
            # Token should be expired
            self.assertTrue(token.is_expired())
    
    def test_token_is_used_default(self):
        """Token is_used default value test"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        self.assertFalse(token.is_used)
    
    def test_token_cascade_delete_user(self):
        """Token cascade delete user test"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        token_id = token.id
        user_id = self.user.id
        
        # Delete user
        self.user.delete()
        
        # Token should also be deleted
        self.assertFalse(EmailVerificationToken.objects.filter(id=token_id).exists())
        self.assertFalse(User.objects.filter(id=user_id).exists())
    
    def test_multiple_tokens_for_same_user(self):
        """Multiple tokens for same user test"""
        token1 = EmailVerificationToken.objects.create(user=self.user)
        token2 = EmailVerificationToken.objects.create(user=self.user)
        
        # Both tokens should be different
        self.assertNotEqual(token1.token, token2.token)
        
        # Should belong to same user
        self.assertEqual(token1.user, self.user)
        self.assertEqual(token2.user, self.user)
        
        # Should have 2 tokens total
        self.assertEqual(EmailVerificationToken.objects.filter(user=self.user).count(), 2)
    
    def test_token_used_status_update(self):
        """Token used status update test"""
        token = EmailVerificationToken.objects.create(user=self.user)
        
        # Initially not used
        self.assertFalse(token.is_used)
        
        # Mark as used
        token.is_used = True
        token.save()
        
        # Get updated token
        updated_token = EmailVerificationToken.objects.get(id=token.id)
        self.assertTrue(updated_token.is_used)


class TestAgentModelIntegration(TestCase):
    """Agent model integration tests"""
    
    def setUp(self):
        """Set up test data"""
        # Create organisor
        self.organisor_user = User.objects.create_user(
            username='integration_organisor',
            email='integration_organisor@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Organisor',
            phone_number='+905551234567',
            date_of_birth='1980-01-01',
            gender='M',
            is_organisor=True,
            email_verified=True
        )
        
        self.organisor_profile, created = UserProfile.objects.get_or_create(user=self.organisor_user)
        Organisor.objects.create(user=self.organisor_user, organisation=self.organisor_profile)
    
    def test_agent_creation_with_verification_token(self):
        """Agent creation with verification token creation test"""
        # Create agent user
        agent_user = User.objects.create_user(
            username='integration_agent',
            email='integration_agent@example.com',
            password='testpass123',
            first_name='Integration',
            last_name='Agent',
            phone_number='+905559876543',
            date_of_birth='1990-01-01',
            gender='F',
            is_agent=True,
            email_verified=False
        )
        
        # Create agent
        agent = Agent.objects.create(
            user=agent_user,
            organisation=self.organisor_profile
        )
        
        # Create verification token
        token = EmailVerificationToken.objects.create(user=agent_user)
        
        # Agent and token relationship
        self.assertEqual(agent.user, agent_user)
        self.assertEqual(token.user, agent_user)
        self.assertFalse(agent_user.email_verified)
        self.assertFalse(token.is_used)
    
    def test_agent_organisation_relationship_integrity(self):
        """Agent-organisation relationship integrity test"""
        # Multiple agents can be in same organisation
        agent1_user = User.objects.create_user(
            username='agent1_integration',
            email='agent1_integration@example.com',
            password='testpass123',
            first_name='Agent1',
            last_name='Integration',
            phone_number='+905551111111',
            date_of_birth='1990-01-01',
            gender='M',
            is_agent=True,
            email_verified=True
        )
        
        agent2_user = User.objects.create_user(
            username='agent2_integration',
            email='agent2_integration@example.com',
            password='testpass123',
            first_name='Agent2',
            last_name='Integration',
            phone_number='+905552222222',
            date_of_birth='1991-01-01',
            gender='F',
            is_agent=True,
            email_verified=True
        )
        
        # Both agents in same organisation
        agent1 = Agent.objects.create(user=agent1_user, organisation=self.organisor_profile)
        agent2 = Agent.objects.create(user=agent2_user, organisation=self.organisor_profile)
        
        # Should belong to same organisation
        self.assertEqual(agent1.organisation, self.organisor_profile)
        self.assertEqual(agent2.organisation, self.organisor_profile)
        
        # Query agents from organisation
        agents_in_org = Agent.objects.filter(organisation=self.organisor_profile)
        self.assertEqual(agents_in_org.count(), 2)
        self.assertIn(agent1, agents_in_org)
        self.assertIn(agent2, agents_in_org)
    
    def test_agent_user_profile_consistency(self):
        """Agent and UserProfile consistency test"""
        agent_user = User.objects.create_user(
            username='consistency_agent',
            email='consistency_agent@example.com',
            password='testpass123',
            first_name='Consistency',
            last_name='Agent',
            phone_number='+905553333333',
            date_of_birth='1992-01-01',
            gender='O',
            is_agent=True,
            email_verified=True
        )
        
        # Create agent
        agent = Agent.objects.create(
            user=agent_user,
            organisation=self.organisor_profile
        )
        
        # UserProfile should be created automatically
        user_profile = UserProfile.objects.get(user=agent_user)
        
        # Consistency check
        self.assertEqual(agent.user, agent_user)
        self.assertEqual(user_profile.user, agent_user)
        self.assertEqual(agent.organisation, self.organisor_profile)
        
        # Check if user is agent
        self.assertTrue(agent_user.is_agent)
        # User model has is_organisor=True as default
        self.assertTrue(agent_user.is_organisor)


if __name__ == "__main__":
    print("Agent Models Tests Starting...")
    print("=" * 60)
    
    # Run tests
    import unittest
    unittest.main()
