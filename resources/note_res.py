from flask import jsonify
from flask_restful import Resource, abort, reqparse

from data import db_session
from data.review import Review


def abort_if_review_not_found(review_id):
    session = db_session.create_session()
    review = session.query(Review).get(review_id)
    if not review:
        abort(404, message=f"Review {review_id} not found")


parser = reqparse.RequestParser()
parser.add_argument('content', required=True)
parser.add_argument('is_private', type=bool)
parser.add_argument('user_id', required=True, type=int)


class ReviewResource(Resource):
    def get(self, review_id):
        abort_if_review_not_found(review_id)
        session = db_session.create_session()
        review = session.query(Review).get(review_id)
        return jsonify({'review': review.to_dict(
            only=('content', 'user_id', 'is_private'))})

    def delete(self, review_id):
        abort_if_review_not_found(review_id)
        session = db_session.create_session()
        review = session.query(Review).get(review_id)
        session.delete(review)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, review_id):
        abort_if_review_not_found(review_id)
        args = parser.parse_args()
        session = db_session.create_session()
        review = session.query(Review).get(review_id)
        review.content = args['content']
        review.user_id = args['user_id']
        review.is_private = args['is_private']
        session.commit()
        return jsonify({'success': 'OK'})


class ReviewListResource(Resource):
    def get(self):
        session = db_session.create_session()
        review = session.query(Review).all()
        return jsonify({'reviews': [item.to_dict(
            only=('content', 'user.name')) for item in review]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        review = Review(
            content=args['content'],
            user_id=args['user_id'],
            is_private=args['is_private']
        )
        session.add(review)
        session.commit()
        return jsonify({'success': 'OK'})
