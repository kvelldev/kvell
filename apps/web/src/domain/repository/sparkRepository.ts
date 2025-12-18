/**
 * Spark Repository Interface (DIP)
 *
 * Abstract definition of data access operations for Spark entities.
 */

import type {
  AddFuelRequest,
  PostSparkRequest,
  Spark,
} from "@/domain/model/spark";

/**
 * Request payload for posting a reply to a bonfire
 */
export interface PostReplyRequest {
  /**
   * Reply content text
   */
  content: string;

  /**
   * Parent bonfire ID to reply to
   */
  parentBonfireId: string;
}

/**
 * Spark Repository Interface
 */
export interface ISparkRepository {
  /**
   * Post a new spark.
   * @param request - The spark content to post
   * @returns The created spark details
   */
  postSpark(request: PostSparkRequest): Promise<Spark>;

  /**
   * Post a reply to a bonfire.
   * @param request - The reply content and parent bonfire ID
   * @returns The created reply spark details
   */
  postReply(request: PostReplyRequest): Promise<Spark>;

  /**
   * Add fuel to a spark.
   * This operation sends an event to the backend but does not return fuel count
   * to maintain the principle of hiding quantitative evaluation from users.
   * @param request - The spark ID to add fuel
   * @returns void (No data returned to hide fuel count)
   */
  addFuel(request: AddFuelRequest): Promise<void>;
}
