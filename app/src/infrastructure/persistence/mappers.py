from src.infrastructure.persistence.models.user import User as UserModel
from src.infrastructure.persistence.models.child import Child as ChildModel
from src.infrastructure.persistence.models.center import Center as CenterModel
from src.infrastructure.persistence.models.course import Course as CourseModel
from src.infrastructure.persistence.models.subscription import SubscriptionTemplate as SubscriptionTemplateModel, Subscription as SubscriptionModel
from src.infrastructure.persistence.models.payment import Payment as PaymentModel, PaymentRefund as PaymentRefundModel
from src.infrastructure.persistence.models.visit import Visit as VisitModel
from src.infrastructure.persistence.models.review import Review as ReviewModel
from src.infrastructure.persistence.models.teacher import Teacher as TeacherModel

from src.domain.entities import (
    User,
    Child,
    Center,
    Course,
    SubscriptionTemplate,
    Subscription,
    Payment,
    PaymentRefund,
    Visit,
    Review,
    Teacher,
)


class TeacherMapper:
    @staticmethod
    def to_entity(model: TeacherModel) -> Teacher:
        return Teacher(
            id=model.id,
            center_id=model.center_id,
            name=model.name,
            description=model.description,
        )
    
    @staticmethod
    def to_model(entity: Teacher) -> TeacherModel:
        return TeacherModel(
            id=entity.id,
            center_id=entity.center_id,
            name=entity.name,
            description=entity.description,
        )
    
    @staticmethod
    def update_model(model: TeacherModel, entity: Teacher) -> None:
        model.name = entity.name
        model.description = entity.description


class UserMapper:
    @staticmethod
    def to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            telegram_id=model.telegram_id,
            username=model.username,
            first_name=model.first_name,
            last_name=model.last_name,
            phone=model.phone,
            city=model.city,
            role=model.role,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_deleted=model.is_deleted,
        )
    
    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            telegram_id=entity.telegram_id,
            username=entity.username,
            first_name=entity.first_name,
            last_name=entity.last_name,
            phone=entity.phone,
            city=entity.city,
            role=entity.role,
        )
    
    @staticmethod
    def update_model(model: UserModel, entity: User) -> None:
        model.username = entity.username
        model.first_name = entity.first_name
        model.last_name = entity.last_name
        model.phone = entity.phone
        model.city = entity.city
        model.role = entity.role


class ChildMapper:
    @staticmethod
    def to_entity(model: ChildModel) -> Child:
        return Child(
            id=model.id,
            parent_id=model.parent_id,
            name=model.name,
            age=model.age,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: Child) -> ChildModel:
        return ChildModel(
            id=entity.id,
            parent_id=entity.parent_id,
            name=entity.name,
            age=entity.age,
        )
    
    @staticmethod
    def update_model(model: ChildModel, entity: Child) -> None:
        model.name = entity.name
        model.age = entity.age


class CenterMapper:
    @staticmethod
    def to_entity(model: CenterModel) -> Center:
        return Center(
            id=model.id,
            partner_id=model.partner_id,
            name=model.name,
            city=model.city,
            address=model.address,
            phone=model.phone,
            category=model.category,
            description=model.description,
            logo=model.logo,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: Center) -> CenterModel:
        return CenterModel(
            id=entity.id,
            partner_id=entity.partner_id,
            name=entity.name,
            city=entity.city,
            address=entity.address,
            phone=entity.phone,
            category=entity.category,
            description=entity.description,
            logo=entity.logo,
            status=entity.status,
        )
    
    @staticmethod
    def update_model(model: CenterModel, entity: Center) -> None:
        model.name = entity.name
        model.city = entity.city
        model.address = entity.address
        model.phone = entity.phone
        model.category = entity.category
        model.description = entity.description
        model.logo = entity.logo
        model.status = entity.status


class CourseMapper:
    @staticmethod
    def to_entity(model: CourseModel) -> Course:
        return Course(
            id=model.id,
            center_id=model.center_id,
            name=model.name,
            description=model.description,
            category=model.category,
            age_min=model.age_min,
            age_max=model.age_max,
            requirements=model.requirements,
            schedule=model.schedule,
            rating=model.rating,
            price_4=model.price_4,
            price_8=model.price_8,
            price_unlimited=model.price_unlimited,
            photo=model.photo,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: Course) -> CourseModel:
        return CourseModel(
            id=entity.id,
            center_id=entity.center_id,
            name=entity.name,
            description=entity.description,
            category=entity.category,
            age_min=entity.age_min,
            age_max=entity.age_max,
            requirements=entity.requirements,
            schedule=entity.schedule,
            rating=entity.rating,
            price_4=entity.price_4,
            price_8=entity.price_8,
            price_unlimited=entity.price_unlimited,
            photo=entity.photo,
        )
    
    @staticmethod
    def update_model(model: CourseModel, entity: Course) -> None:
        model.name = entity.name
        model.description = entity.description
        model.category = entity.category
        model.age_min = entity.age_min
        model.age_max = entity.age_max
        model.requirements = entity.requirements
        model.schedule = entity.schedule
        model.rating = entity.rating
        model.price_4 = entity.price_4
        model.price_8 = entity.price_8
        model.price_unlimited = entity.price_unlimited
        model.photo = entity.photo


class SubscriptionTemplateMapper:
    @staticmethod
    def to_entity(model: SubscriptionTemplateModel) -> SubscriptionTemplate:
        return SubscriptionTemplate(
            id=model.id,
            name=model.name,
            description=model.description,
            tariff=model.tariff,
            lessons_total=model.lessons_total,
            price=model.price,
            is_active=model.is_active,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: SubscriptionTemplate) -> SubscriptionTemplateModel:
        return SubscriptionTemplateModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            tariff=entity.tariff,
            lessons_total=entity.lessons_total,
            price=entity.price,
            is_active=entity.is_active,
            created_by=entity.created_by,
        )
    
    @staticmethod
    def update_model(model: SubscriptionTemplateModel, entity: SubscriptionTemplate) -> None:
        model.name = entity.name
        model.description = entity.description
        model.price = entity.price
        model.is_active = entity.is_active


class SubscriptionMapper:
    @staticmethod
    def to_entity(model: SubscriptionModel) -> Subscription:
        return Subscription(
            id=model.id,
            user_id=model.user_id,
            child_id=model.child_id,
            template_id=model.template_id,
            tariff=model.tariff,
            lessons_total=model.lessons_total,
            lessons_remaining=model.lessons_remaining,
            qr_code=model.qr_code,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: Subscription) -> SubscriptionModel:
        return SubscriptionModel(
            id=entity.id,
            user_id=entity.user_id,
            child_id=entity.child_id,
            template_id=entity.template_id,
            tariff=entity.tariff,
            lessons_total=entity.lessons_total,
            lessons_remaining=entity.lessons_remaining,
            qr_code=entity.qr_code,
            status=entity.status,
        )
    
    @staticmethod
    def update_model(model: SubscriptionModel, entity: Subscription) -> None:
        model.lessons_remaining = entity.lessons_remaining
        model.status = entity.status


class PaymentMapper:
    @staticmethod
    def to_entity(model: PaymentModel) -> Payment:
        return Payment(
            id=model.id,
            subscription_id=model.subscription_id,
            user_id=model.user_id,
            amount=model.amount,
            currency=model.currency,
            method=model.method,
            status=model.status,
            transaction_id=model.transaction_id,
            invoice_id=model.invoice_id,
            airba_payment_id=model.airba_payment_id,
            redirect_url=model.redirect_url,
            error_message=model.error_message,
            created_at=model.created_at,
            updated_at=model.updated_at,
            processed_at=model.processed_at,
        )
    
    @staticmethod
    def to_model(entity: Payment) -> PaymentModel:
        return PaymentModel(
            id=entity.id,
            user_id=entity.user_id,
            subscription_id=entity.subscription_id,
            amount=entity.amount,
            currency=entity.currency,
            method=entity.method,
            status=entity.status,
            transaction_id=entity.transaction_id,
            invoice_id=entity.invoice_id,
            airba_payment_id=entity.airba_payment_id,
            redirect_url=entity.redirect_url,
            error_message=entity.error_message,
            processed_at=entity.processed_at,
        )
    
    @staticmethod
    def update_model(model: PaymentModel, entity: Payment) -> None:
        model.status = entity.status
        model.transaction_id = entity.transaction_id
        model.error_message = entity.error_message
        model.processed_at = entity.processed_at


class PaymentRefundMapper:
    @staticmethod
    def to_entity(model: PaymentRefundModel) -> PaymentRefund:
        return PaymentRefund(
            id=model.id,
            payment_id=model.payment_id,
            airba_refund_id=model.airba_refund_id,
            ext_id=model.ext_id,
            amount=model.amount,
            reason=model.reason,
            status=model.status,
            processed_at=model.processed_at,
        )
    
    @staticmethod
    def to_model(entity: PaymentRefund) -> PaymentRefundModel:
        return PaymentRefundModel(
            id=entity.id,
            payment_id=entity.payment_id,
            airba_refund_id=entity.airba_refund_id,
            ext_id=entity.ext_id,
            amount=entity.amount,
            reason=entity.reason,
            status=entity.status,
        )


class VisitMapper:
    @staticmethod
    def to_entity(model: VisitModel) -> Visit:
        return Visit(
            id=model.id,
            subscription_id=model.subscription_id,
            user_id=model.user_id,
            child_id=model.child_id,
            center_id=model.center_id,
            lesson_id=model.lesson_id,
            visited_at=model.visited_at,
        )
    
    @staticmethod
    def to_model(entity: Visit) -> VisitModel:
        return VisitModel(
            id=entity.id,
            subscription_id=entity.subscription_id,
            user_id=entity.user_id,
            child_id=entity.child_id,
            center_id=entity.center_id,
            lesson_id=entity.lesson_id,
        )


class ReviewMapper:
    @staticmethod
    def to_entity(model: ReviewModel) -> Review:
        return Review(
            id=model.id,
            course_id=model.course_id,
            user_id=model.user_id,
            rating=model.rating,
            comment=model.comment,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: Review) -> ReviewModel:
        return ReviewModel(
            id=entity.id,
            course_id=entity.course_id,
            user_id=entity.user_id,
            rating=entity.rating,
            comment=entity.comment,
        )
    
    @staticmethod
    def update_model(model: ReviewModel, entity: Review) -> None:
        model.rating = entity.rating
        model.comment = entity.comment
