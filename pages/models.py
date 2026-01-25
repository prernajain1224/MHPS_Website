from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.search import index
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from wagtail.images.models import Image
from collections import OrderedDict
import math
from modelcluster.fields import ParentalKey
from datetime import datetime


class ContactPage(Page):
    template = "pages/contact_page.html"

    page_title = models.CharField(max_length=100, default="Contact Us")
    page_subtitle = models.CharField(max_length=255, blank=True)

    introduction = RichTextField(blank=True)

    office_address = RichTextField(blank=True)

    phone_primary = models.CharField(max_length=20, blank=True)
    phone_secondary = models.CharField(max_length=20, blank=True)

    email_primary = models.EmailField(blank=True)
    email_secondary = models.EmailField(blank=True)

    office_hours = RichTextField(blank=True)

    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)

    map_embed_code = models.TextField(blank=True)
    additional_content = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("page_title"),
            FieldPanel("page_subtitle"),
            FieldPanel("introduction"),
        ], heading="Page Header"),

        MultiFieldPanel([
            FieldPanel("office_address"),
            FieldPanel("phone_primary"),
            FieldPanel("phone_secondary"),
            FieldPanel("email_primary"),
            FieldPanel("email_secondary"),
            FieldPanel("office_hours"),
        ], heading="Contact Information"),

        MultiFieldPanel([
            FieldPanel("facebook_url"),
            FieldPanel("twitter_url"),
            FieldPanel("instagram_url"),
            FieldPanel("youtube_url"),
        ], heading="Social Media Links"),

        MultiFieldPanel([
            FieldPanel("map_embed_code"),
        ], heading="Google Maps"),

        MultiFieldPanel([
            FieldPanel("additional_content"),
        ], heading="Additional Content"),
    ]


class PressIndexPage(Page):

    template = "pages/press_index_page.html"
    """
    Press Section Landing Page
    Contains tabs for different press content types
    """
    
    page_title = models.CharField(
        max_length=100,
        default="Press",
        help_text="Main page heading"
    )
    
    introduction = RichTextField(
        blank=True,
        help_text="Introduction text (optional)"
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('page_title'),
        FieldPanel('introduction'),
    ]
    
    # Only allow PressReleasePage, NewsPage, etc. as children
    subpage_types = [
        'pages.PressReleasePage',
        'pages.NewsPage',
        'pages.InterviewPage',
        'pages.EditorialPage',
    ]
    
    class Meta:
        verbose_name = "Press Index Page"
    
    def get_context(self, request):
        context = super().get_context(request)
        
        # Get active tab from query parameter (default: press-releases)
        active_tab = request.GET.get('tab', 'press-releases')
        context['active_tab'] = active_tab
        
        # Get all press releases
        press_releases = PressReleasePage.objects.live().child_of(self).order_by('-press_date')
        
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(press_releases, 9)  # 9 items per page (3x3 grid)
        
        try:
            press_releases = paginator.page(page)
        except PageNotAnInteger:
            press_releases = paginator.page(1)
        except EmptyPage:
            press_releases = paginator.page(paginator.num_pages)
        
        context['press_releases'] = press_releases
        
        return context


class PressReleasePage(Page):
    template = "pages/press_release_page.html"
    
    """
    Individual Press Release Page
    """
    
    # Press Release Date
    press_date = models.DateField(
        help_text="Date of press release"
    )
    
    # Author/Speaker Names
    author_names = models.CharField(
        max_length=255,
        help_text="Author or speaker names (comma separated if multiple)",
        blank=True
    )
    
    # Short Title for Card Display
    short_title = models.CharField(
        max_length=255,
        help_text="Short title for card display"
    )
    
    # Full Content
    content = RichTextField(
        help_text="Full press release content"
    )
    
    # Featured Flag
    is_featured = models.BooleanField(
        default=False,
        help_text="Mark as featured (will be highlighted with green background)"
    )
    
    # Search Index
    search_fields = Page.search_fields + [
        index.SearchField('short_title'),
        index.SearchField('content'),
        index.SearchField('author_names'),
    ]
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('press_date'),
            FieldPanel('author_names'),
            FieldPanel('short_title'),
            FieldPanel('is_featured'),
        ], heading="Press Release Info"),
        
        FieldPanel('content'),
    ]
    
    parent_page_types = ['pages.PressIndexPage']
    
    class Meta:
        verbose_name = "Press Release"
        verbose_name_plural = "Press Releases"
        ordering = ['-press_date']


class NewsPage(Page):
    template = "pages/news_page.html"
    """News Page - Similar structure to Press Release"""
    
    press_date = models.DateField(help_text="Date of news")
    author_names = models.CharField(max_length=255, blank=True)
    short_title = models.CharField(max_length=255)
    content = RichTextField()
    is_featured = models.BooleanField(default=False)
    
    search_fields = Page.search_fields + [
        index.SearchField('short_title'),
        index.SearchField('content'),
    ]
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('press_date'),
            FieldPanel('author_names'),
            FieldPanel('short_title'),
            FieldPanel('is_featured'),
        ], heading="News Info"),
        FieldPanel('content'),
    ]
    
    parent_page_types = ['pages.PressIndexPage']
    
    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"
        ordering = ['-press_date']


class InterviewPage(Page):
    template = "pages/interview_page.html"
    """Interview Page"""
    
    press_date = models.DateField(help_text="Date of interview")
    author_names = models.CharField(max_length=255, blank=True)
    short_title = models.CharField(max_length=255)
    content = RichTextField()
    is_featured = models.BooleanField(default=False)
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('press_date'),
            FieldPanel('author_names'),
            FieldPanel('short_title'),
            FieldPanel('is_featured'),
        ], heading="Interview Info"),
        FieldPanel('content'),
    ]
    
    parent_page_types = ['pages.PressIndexPage']
    
    class Meta:
        verbose_name = "Interview"
        ordering = ['-press_date']


class EditorialPage(Page):
    template = "pages/editorial_page.html"
    """Editorial Page"""
    
    press_date = models.DateField(help_text="Date of editorial")
    author_names = models.CharField(max_length=255, blank=True)
    short_title = models.CharField(max_length=255)
    content = RichTextField()
    is_featured = models.BooleanField(default=False)
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('press_date'),
            FieldPanel('author_names'),
            FieldPanel('short_title'),
            FieldPanel('is_featured'),
        ], heading="Editorial Info"),
        FieldPanel('content'),
    ]
    
    parent_page_types = ['pages.PressIndexPage']
    
    class Meta:
        verbose_name = "Editorial"
        ordering = ['-press_date']



class EventIndexPage(Page):

    template = "pages/event_index_page.html"
    """
    Events Landing Page
    Shows Upcoming and Past events with filters
    """
    
    page_title = models.CharField(
        max_length=100,
        default="Events",
        help_text="Main page heading"
    )
    
    introduction = RichTextField(
        blank=True,
        help_text="Introduction text about events"
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('page_title'),
        FieldPanel('introduction'),
    ]
    
    subpage_types = ['pages.EventPage']
    
    class Meta:
        verbose_name = "Event Index Page"
    
    def get_context(self, request):
        context = super().get_context(request)
        
        # Get active tab (upcoming or past)
        active_tab = request.GET.get('tab', 'upcoming')
        context['active_tab'] = active_tab
        
        # Get all events
        all_events = EventPage.objects.live().child_of(self).order_by('event_start_date', 'event_start_time')
        
        # Filter by tab
        now = timezone.now()
        if active_tab == 'upcoming':
            events = all_events.filter(event_start_date__gte=now.date()).order_by('event_start_date', 'event_start_time')
        else:  # past
            events = all_events.filter(event_start_date__lt=now.date()).order_by('-event_start_date', '-event_start_time')
        
        # Apply filters from query parameters
        event_type = request.GET.get('event_type')
        event_format = request.GET.get('event_format')
        has_livestream = request.GET.get('livestream')
        
        if event_type:
            events = events.filter(event_type=event_type)
        
        if event_format:
            events = events.filter(event_format=event_format)
        
        if has_livestream == 'true':
            events = events.filter(has_livestream=True)
        
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(events, 9)  # 9 events per page (3x3 grid)
        
        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            events = paginator.page(1)
        except EmptyPage:
            events = paginator.page(paginator.num_pages)
        
        context['events'] = events
        
        # Get unique values for filters
        context['event_types'] = EventPage.EVENT_TYPE_CHOICES
        context['event_formats'] = EventPage.EVENT_FORMAT_CHOICES
        
        return context


class EventPage(Page):
    template = "pages/event_page.html"
    """
    Individual Event Page
    """
    
    # Event Type Choices
    EVENT_TYPE_CHOICES = [
        ('lecture', 'Lecture'),
        ('webinar', 'Webinar'),
        ('panel', 'Panel'),
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('seminar', 'Seminar'),
    ]
    
    # Event Format Choices
    EVENT_FORMAT_CHOICES = [
        ('hybrid', 'Hybrid'),
        ('online', 'Online'),
        ('in-person', 'In-Person'),
    ]
    
    # Event Details
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES,
        default='lecture',
        help_text="Type of event"
    )
    
    event_format = models.CharField(
        max_length=50,
        choices=EVENT_FORMAT_CHOICES,
        default='hybrid',
        help_text="Event format"
    )
    
    has_livestream = models.BooleanField(
        default=False,
        help_text="Does this event have livestream?"
    )
    
    # Date & Time
    event_start_date = models.DateField(
        help_text="Event start date"
    )
    
    event_start_time = models.TimeField(
        help_text="Event start time"
    )
    
    event_end_time = models.TimeField(
        help_text="Event end time"
    )
    
    # Event Content
    event_title = models.CharField(
        max_length=255,
        help_text="Event title"
    )
    
    short_description = models.TextField(
        max_length=300,
        help_text="Short description for card display (max 300 characters)"
    )
    
    full_description = RichTextField(
        help_text="Full event description and details"
    )
    
    # Additional Info
    event_location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Event location (if in-person or hybrid)"
    )
    
    registration_link = models.URLField(
        blank=True,
        help_text="External registration link (optional)"
    )
    
    # Search Index
    search_fields = Page.search_fields + [
        index.SearchField('event_title'),
        index.SearchField('short_description'),
        index.SearchField('full_description'),
    ]
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('event_type'),
            FieldPanel('event_format'),
            FieldPanel('has_livestream'),
        ], heading="Event Type & Format"),
        
        MultiFieldPanel([
            FieldPanel('event_start_date'),
            FieldPanel('event_start_time'),
            FieldPanel('event_end_time'),
            FieldPanel('event_location'),
        ], heading="Date, Time & Location"),
        
        MultiFieldPanel([
            FieldPanel('event_title'),
            FieldPanel('short_description'),
            FieldPanel('full_description'),
        ], heading="Event Content"),
        
        MultiFieldPanel([
            FieldPanel('registration_link'),
        ], heading="Registration"),
    ]
    
    parent_page_types = ['pages.EventIndexPage']
    
    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ['event_start_date', 'event_start_time']
    
    def is_upcoming(self):
        """Check if event is upcoming"""
        now = timezone.now()
        return self.event_start_date >= now.date()
    
    def formatted_date_time(self):
        """Return formatted date and time string"""
        return f"{self.event_start_date.strftime('%B %Y')} — {self.event_start_time.strftime('%I:%M%p')} TO {self.event_end_time.strftime('%I:%M%p')}"
    

class AboutPage(Page):
    template = "pages/aboutus.html"
    """
    About Page with Timeline
    Timeline periods auto-generate based on historical events
    """
    
    page_title = models.CharField(
        max_length=100,
        default="About Us",
        help_text="Main page heading"
    )
    
    introduction = RichTextField(
        blank=True,
        help_text="Introduction text (optional)"
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('page_title'),
        FieldPanel('introduction'),
    ]
    
    subpage_types = ['pages.HistoricalEventPage']
    
    class Meta:
        verbose_name = "About Page"
    
    def get_timeline_periods(self):
        """
        Auto-generate timeline periods based on historical events
        Groups events into 5-year periods
        Returns only periods that have events
        """
        # Get all historical events
        events = HistoricalEventPage.objects.live().child_of(self).order_by('event_date')
        
        if not events:
            return []
        
        periods = OrderedDict()
        
        for event in events:
            year = event.event_date.year
            # Calculate period start (round down to nearest 5-year period ending in 0 or 5)
            period_start = (year // 5) * 5
            period_end = period_start + 5
            
            period_key = f"{period_start}-{period_end}"
            
            if period_key not in periods:
                periods[period_key] = {
                    'start': period_start,
                    'end': period_end,
                    'label': f"{period_start} - {period_end}",
                    'count': 0
                }
            
            periods[period_key]['count'] += 1
        
        return list(periods.values())
    
    def get_context(self, request):
        context = super().get_context(request)
        
        # Get selected period from query parameter
        selected_period = request.GET.get('period', 'all')
        context['selected_period'] = selected_period
        
        # Get all historical events
        events = HistoricalEventPage.objects.live().child_of(self).order_by('-event_date')
        
        # Filter by period if selected
        if selected_period != 'all':
            try:
                start_year, end_year = selected_period.split('-')
                start_year = int(start_year)
                end_year = int(end_year)
                events = events.filter(
                    event_date__year__gte=start_year,
                    event_date__year__lt=end_year
                )
            except (ValueError, AttributeError):
                pass  # Invalid period, show all
        
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(events, 10)  # 10 events per page
        
        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            events = paginator.page(1)
        except EmptyPage:
            events = paginator.page(paginator.num_pages)
        
        context['events'] = events
        context['timeline_periods'] = self.get_timeline_periods()
        
        return context


class HistoricalEventPage(Page):
    template = "pages/historical_event_page.html"
    """
    Individual Historical Event
    """
    
    # Event Date
    event_date = models.DateField(
        help_text="Date of the historical event"
    )
    
    # Event Image
    event_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Event image (recommended: 1200x800px)"
    )
    
    # Event Title
    event_title = models.CharField(
        max_length=255,
        help_text="Event title/heading"
    )
    
    # Event Description
    event_description = RichTextField(
        help_text="Full event description"
    )
    
    # Search Index
    search_fields = Page.search_fields + [
        index.SearchField('event_title'),
        index.SearchField('event_description'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel('event_date'),
        FieldPanel('event_image'),
        FieldPanel('event_title'),
        FieldPanel('event_description'),
    ]
    
    parent_page_types = ['pages.AboutPage']
    
    class Meta:
        verbose_name = "Historical Event"
        verbose_name_plural = "Historical Events"
        ordering = ['-event_date']
    
    def get_period_label(self):
        """Get the 5-year period this event belongs to"""
        year = self.event_date.year
        period_start = (year // 5) * 5
        period_end = period_start + 5
        return f"{period_start}-{period_end}"
    



class GalleryIndexPage(Page):
    template = "pages/gallery_index_page.html"
    """
    Photo Gallery Index Page
    Shows all photo albums in masonry grid
    """
    
    page_title = models.CharField(
        max_length=100,
        default="Photo Gallery",
        help_text="Main page heading"
    )
    
    introduction = RichTextField(
        blank=True,
        help_text="Introduction text (optional)"
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('page_title'),
        FieldPanel('introduction'),
    ]
    
    subpage_types = ['pages.GalleryAlbumPage']
    
    class Meta:
        verbose_name = "Gallery Index Page"
    
    def get_context(self, request):
        context = super().get_context(request)
        
        # Get all albums
        albums = GalleryAlbumPage.objects.live().child_of(self).order_by('-album_date')
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            albums = albums.search(search_query)
        
        # Date range filtering
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                albums = albums.filter(album_date__gte=from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                albums = albums.filter(album_date__lte=to_date)
            except ValueError:
                pass
        
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(albums, 12)  # 12 albums per page
        
        try:
            albums = paginator.page(page)
        except PageNotAnInteger:
            albums = paginator.page(1)
        except EmptyPage:
            albums = paginator.page(paginator.num_pages)
        
        context['albums'] = albums
        context['search_query'] = search_query
        context['date_from'] = date_from
        context['date_to'] = date_to
        
        return context


class GalleryAlbumPage(Page):
    template = "pages/gallery_album_page.html"
    """
    Individual Photo Album/Folder
    Contains multiple photos
    """
    
    # Album Details
    album_title = models.CharField(
        max_length=255,
        help_text="Album title/name"
    )
    
    album_date = models.DateField(
        help_text="Album date (for sorting and filtering)"
    )
    
    album_description = RichTextField(
        blank=True,
        help_text="Album description (optional)"
    )
    
    # Cover Image (first image or manually selected)
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Album cover image (if not set, first photo will be used)"
    )
    
    # Search Index
    search_fields = Page.search_fields + [
        index.SearchField('album_title'),
        index.SearchField('album_description'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel('album_title'),
        FieldPanel('album_date'),
        FieldPanel('cover_image'),
        FieldPanel('album_description'),
        InlinePanel('gallery_images', label="Photos", min_num=1),
    ]
    
    parent_page_types = ['pages.GalleryIndexPage']
    
    class Meta:
        verbose_name = "Gallery Album"
        verbose_name_plural = "Gallery Albums"
        ordering = ['-album_date']
    
    def get_cover_image(self):
        """Get cover image or first photo"""
        if self.cover_image:
            return self.cover_image
        
        first_image = self.gallery_images.first()
        if first_image:
            return first_image.image
        
        return None
    
    def get_photo_count(self):
        """Get total number of photos in album"""
        return self.gallery_images.count()


class GalleryImage(Orderable):
    """
    Individual photo in an album
    """
    
    page = ParentalKey(
        GalleryAlbumPage,
        on_delete=models.CASCADE,
        related_name='gallery_images'
    )
    
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+'
    )
    
    caption = models.CharField(
        max_length=255,
        blank=True,
        help_text="Photo caption (optional)"
    )
    
    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]
    
    class Meta:
        verbose_name = "Gallery Image"
        verbose_name_plural = "Gallery Images"


class ArticleIndexPage(Page):
    template = "pages/article_index__page.html"
    """
    Articles Landing Page
    Similar to Events but for published articles
    """
    
    page_title = models.CharField(
        max_length=100,
        default="Articles",
        help_text="Main page heading"
    )
    
    introduction = RichTextField(
        blank=True,
        help_text="Introduction text (optional)"
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('page_title'),
        FieldPanel('introduction'),
    ]
    
    subpage_types = ['pages.ArticlePage']
    
    class Meta:
        verbose_name = "Article Index Page"
    
    def get_context(self, request):
        context = super().get_context(request)
        
        # Get all articles
        articles = ArticlePage.objects.live().child_of(self).order_by('-publish_date')
        
        # Apply filters
        article_type = request.GET.get('article_type')
        
        if article_type:
            articles = articles.filter(article_type=article_type)
        
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(articles, 9)
        
        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)
        
        context['articles'] = articles
        context['article_types'] = ArticlePage.ARTICLE_TYPE_CHOICES
        
        return context


class ArticlePage(Page):
    template = "pages/article__page.html"
    """
    Individual Article Page
    """
    
    ARTICLE_TYPE_CHOICES = [
        ('analysis', 'Analysis'),
        ('opinion', 'Opinion'),
        ('research', 'Research'),
        ('commentary', 'Commentary'),
        ('report', 'Report'),
    ]
    
    article_type = models.CharField(
        max_length=50,
        choices=ARTICLE_TYPE_CHOICES,
        default='analysis',
        help_text="Type of article"
    )
    
    publish_date = models.DateField(
        help_text="Article publish date"
    )
    
    publish_time = models.TimeField(
        default='09:00',
        help_text="Article publish time"
    )
    
    author_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Article author name"
    )
    
    article_title = models.CharField(
        max_length=255,
        help_text="Article title"
    )
    
    short_description = models.TextField(
        max_length=300,
        help_text="Short description for card display"
    )
    
    full_content = RichTextField(
        help_text="Full article content"
    )
    
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Featured article image"
    )
    
    is_featured = models.BooleanField(
        default=False,
        help_text="Mark as featured article"
    )
    
    search_fields = Page.search_fields + [
        index.SearchField('article_title'),
        index.SearchField('short_description'),
        index.SearchField('full_content'),
        index.SearchField('author_name'),
    ]
    
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('article_type'),
            FieldPanel('is_featured'),
        ], heading="Article Type"),
        
        MultiFieldPanel([
            FieldPanel('publish_date'),
            FieldPanel('publish_time'),
            FieldPanel('author_name'),
        ], heading="Publication Details"),
        
        MultiFieldPanel([
            FieldPanel('article_title'),
            FieldPanel('short_description'),
            FieldPanel('featured_image'),
            FieldPanel('full_content'),
        ], heading="Article Content"),
    ]
    
    parent_page_types = ['pages.ArticleIndexPage']
    
    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-publish_date']


class PressGalleryIndexPage(Page):
    template = "pages/press_gallery_index_page.html"
    """
    Press Gallery Index Page
    For editorial photos, election rallies, government events, etc.
    """
    
    page_title = models.CharField(
        max_length=100,
        default="Press Gallery",
        help_text="Main page heading"
    )
    
    introduction = RichTextField(
        blank=True,
        help_text="Introduction text (optional)"
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('page_title'),
        FieldPanel('introduction'),
    ]
    
    subpage_types = ['pages.PressGalleryCategoryPage']
    
    class Meta:
        verbose_name = "Press Gallery Index Page"
    
    def get_context(self, request):
        context = super().get_context(request)
        
        # Get all categories
        categories = PressGalleryCategoryPage.objects.live().child_of(self).order_by('title')
        context['categories'] = categories
        
        return context


class PressGalleryCategoryPage(Page):
    template = "pages/press_gallery_category_page.html"
    """
    Press Gallery Category (Editorials, Election Rally, Government Events, etc.)
    """
    
    category_name = models.CharField(
        max_length=100,
        help_text="Category name (e.g., Editorials, Election Rally)"
    )
    
    category_description = RichTextField(
        blank=True,
        help_text="Category description (optional)"
    )
    
    content_panels = Page.content_panels + [
        FieldPanel('category_name'),
        FieldPanel('category_description'),
    ]
    
    parent_page_types = ['pages.PressGalleryIndexPage']
    subpage_types = ['pages.PressAlbumPage']
    
    class Meta:
        verbose_name = "Press Gallery Category"
        verbose_name_plural = "Press Gallery Categories"
    
    def get_context(self, request):
        context = super().get_context(request)
        
        # Get all albums in this category
        albums = PressAlbumPage.objects.live().child_of(self).order_by('-album_date')
        
        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            albums = albums.search(search_query)
        
        # Date range filtering
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        if date_from:
            try:
                from datetime import datetime
                from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
                albums = albums.filter(album_date__gte=from_date)
            except ValueError:
                pass
        
        if date_to:
            try:
                from datetime import datetime
                to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
                albums = albums.filter(album_date__lte=to_date)
            except ValueError:
                pass
        
        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(albums, 12)
        
        try:
            albums = paginator.page(page)
        except PageNotAnInteger:
            albums = paginator.page(1)
        except EmptyPage:
            albums = paginator.page(paginator.num_pages)
        
        context['albums'] = albums
        context['search_query'] = search_query
        context['date_from'] = date_from
        context['date_to'] = date_to
        
        return context
    
    def get_album_count(self):
        """Get total number of albums in category"""
        return PressAlbumPage.objects.live().child_of(self).count()


class PressAlbumPage(Page):
    template = "pages/press_album_page.html"
    
    """
    Individual Press Album/Event
    """
    
    album_title = models.CharField(
        max_length=255,
        help_text="Album title"
    )
    
    album_date = models.DateField(
        help_text="Album date"
    )
    
    album_location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Event location (e.g., Indira Bhawan | New Delhi)"
    )
    
    album_description = RichTextField(
        blank=True,
        help_text="Album description (optional)"
    )
    
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Album cover image"
    )
    
    search_fields = Page.search_fields + [
        index.SearchField('album_title'),
        index.SearchField('album_location'),
        index.SearchField('album_description'),
    ]
    
    content_panels = Page.content_panels + [
        FieldPanel('album_title'),
        FieldPanel('album_date'),
        FieldPanel('album_location'),
        FieldPanel('cover_image'),
        FieldPanel('album_description'),
        InlinePanel('press_images', label="Photos", min_num=1),
    ]
    
    parent_page_types = ['pages.PressGalleryCategoryPage']
    
    class Meta:
        verbose_name = "Press Album"
        verbose_name_plural = "Press Albums"
        ordering = ['-album_date']
    
    def get_cover_image(self):
        """Get cover image or first photo"""
        if self.cover_image:
            return self.cover_image
        
        first_image = self.press_images.first()
        if first_image:
            return first_image.image
        
        return None
    
    def get_photo_count(self):
        """Get total number of photos"""
        return self.press_images.count()


class PressImage(Orderable):
    """
    Individual photo in press album
    """
    
    page = ParentalKey(
        PressAlbumPage,
        on_delete=models.CASCADE,
        related_name='press_images'
    )
    
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+'
    )
    
    caption = models.CharField(
        max_length=255,
        blank=True,
        help_text="Photo caption (optional)"
    )
    
    panels = [
        FieldPanel('image'),
        FieldPanel('caption'),
    ]
    
    class Meta:
        verbose_name = "Press Image"
        verbose_name_plural = "Press Images"